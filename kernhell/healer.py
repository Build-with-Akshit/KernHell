"""
The Healer Engine v2.
Orchestrates AI providers with:
- Screenshot-enhanced diagnosis (Vision AI)
- Key rotation + provider failover
- Optimized single-shot accuracy
- Healing Memory (learn from past fixes)
- Semantic Selector Fallback (ChromaDB)
"""
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
from kernhell.core.config import config, CONFIG_DIR
from kernhell.providers import get_provider_fn, get_model_name, supports_vision
from kernhell.utils import log_info, log_warning, log_error, log_success, console
from typing import Optional, Dict, List


class HealingMemory:
    """Remember past fixes to avoid repeating mistakes"""
    
    def __init__(self):
        self.memory_file = CONFIG_DIR / "healing_history.json"
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load healing history from disk"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_history(self):
        """Save healing history to disk"""
        try:
            # Keep only last 100 entries to prevent bloat
            if len(self.history) > 100:
                self.history = self.history[-100:]
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass  # Fail silently if can't save
    
    def remember(self, error: str, fix: str, success: bool, provider: str = None):
        """Store fix attempt"""
        error_hash = hashlib.md5(error.encode()).hexdigest()
        
        self.history.append({
            'error_hash': error_hash,
            'error_snippet': error[:300],  # Store snippet for matching
            'fix': fix,
            'success': success,
            'provider': provider,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_history()
    
    def recall_similar(self, error: str, threshold: float = 0.7) -> Optional[str]:
        """
        Find similar successful fixes using fuzzy matching.
        Returns the fix code if a good match is found.
        """
        best_match = None
        best_score = 0.0
        
        # Search in reverse (most recent first)
        for entry in reversed(self.history):
            # Only consider successful fixes
            if not entry.get('success', False):
                continue
            
            # Calculate similarity
            similarity = SequenceMatcher(
                None, 
                error.lower(), 
                entry['error_snippet'].lower()
            ).ratio()
            
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = entry['fix']
        
        if best_match:
            log_success(f"💾 Found similar fix in memory (similarity: {best_score:.1%})")
        
        return best_match


# Global healing memory instance
healing_memory = HealingMemory()


def get_ai_fix(code_content: str, error_log: str, screenshot_b64: str = None, feedback_context: str = "") -> str:
    """
    Multi-Provider AI Fix Engine with Vision Support and Healing Memory.
    Accepts optional feedback_context for retry loops.
    """
    # Check healing memory first (skip if this is a retry)
    if not feedback_context:
        remembered_fix = healing_memory.recall_similar(error_log)
        if remembered_fix:
            log_info("Using fix from healing memory instead of calling AI")
            return remembered_fix
    
    total_keys = config.get_key_count()
    if total_keys == 0:
        raise ValueError("No API Keys found! Run `kernhell config add-key <KEY> --provider <name>` first.")

    # Smart Router: Auto-select best provider based on task context
    best_provider = _router_select_provider(has_vision=bool(screenshot_b64))
    
    # DEBUG: Help diagnose empty provider logs
    if best_provider:
        log_info(f"Router suggests: '{best_provider}'")

    if best_provider and best_provider != config.current_provider:
        # Switch if the best provider is available and different
        if config.provider_keys.get(best_provider):
             log_info(f"Smart Switch: Routing to [{best_provider}] for optimized handling.")
             config.current_provider = best_provider
             config.current_key_index = 0

    providers_tried = set()
    max_provider_attempts = len(config.get_all_providers_with_keys()) + 1

    for _ in range(max_provider_attempts):
        provider = config.current_provider
        if provider in providers_tried:
            new_provider = config.switch_provider()
            if not new_provider or new_provider in providers_tried:
                break
            provider = new_provider

        providers_tried.add(provider)
        provider_fn = get_provider_fn(provider)
        model_name = get_model_name(provider)
        keys = config.provider_keys.get(provider, [])

        if not keys or not provider_fn:
            log_warning(f"No keys or unsupported provider: {provider}. Skipping...")
            new_provider = config.switch_provider()
            if not new_provider:
                break
            continue

        # Determine if we should send screenshot to this provider
        use_vision = screenshot_b64 and supports_vision(provider)
        mode_label = "Vision" if use_vision else "Text"
        retry_label = " [RETRY MODE]" if feedback_context else ""
        log_info(f"Consulting {model_name} via [{provider}] ({mode_label}{retry_label})...")

        # Try each key in this provider
        for attempt in range(len(keys) * 2):
            active_key = config.get_active_key()
            if not active_key:
                break

            try:
                # Append feedback to error log if present
                full_error_log = error_log
                if feedback_context:
                    full_error_log = f"{error_log}\n\n=== PREVIOUS FAILED FIX ATTEMPT ===\n{feedback_context}"

                fix = provider_fn(
                    code_content,
                    full_error_log,
                    active_key,
                    screenshot_b64=screenshot_b64 if use_vision else None
                )
                if fix:
                    # Track quota usage
                    config.record_api_call(provider)
                    
                    # Remember this fix
                    healing_memory.remember(
                        error=error_log,
                        fix=fix,
                        success=True,
                        provider=provider
                    )
                    return fix
                else:
                    log_warning(f"Empty response from {provider}. Rotating key...")
                    config.rotate_key()

            except Exception as e:
                error_msg = str(e)
                log_warning(f"[{provider}] Key #{config.current_key_index + 1} Error: {error_msg[:200]}")
                config.rotate_key()

                if (attempt + 1) >= len(keys):
                    log_warning(f"All [{provider}] keys exhausted. Trying next provider...")
                    break

        new_provider = config.switch_provider()
        if not new_provider:
            break

    raise RuntimeError(
        "All providers and keys exhausted! Add more keys:\n"
        "  kernhell config add-key <KEY> --provider google\n"
        "  kernhell config add-key <KEY> --provider groq\n"
        "  kernhell config add-key <KEY> --provider openrouter"
    )


def get_active_model_name() -> str:
    """Returns the model name for the currently active provider."""
    return get_model_name(config.current_provider)


def _router_select_provider(has_vision: bool) -> Optional[str]:
    """
    Decides the optimal provider based on task requirements and key availability.
    Google (Gemini) is preferred for all modes since it's both fast AND accurate.
    Groq is the fast fallback when Google is unavailable.
    """
    available_providers = config.get_all_providers_with_keys()
    
    if has_vision:
        # Vision mode priority: Google (Gemini 2.0 Flash) > NVIDIA > OpenRouter
        if "google" in available_providers: return "google"
        if "nvidia" in available_providers: return "nvidia"
        if "openrouter" in available_providers: return "openrouter"
    
    # Text/general priority: Google > Groq > NVIDIA > Cloudflare > OpenRouter
    if "google" in available_providers: return "google"
    if "groq" in available_providers: return "groq"
    if "nvidia" in available_providers: return "nvidia"
    if "cloudflare" in available_providers: return "cloudflare"
    if "openrouter" in available_providers: return "openrouter"
    
    return None


def _extract_selector_from_error(error: str) -> Optional[str]:
    """
    Extract failed selector from Playwright error messages.
    
    Handles patterns like:
        selector "#login"
        locator("#submit-btn")
        page.click("#buy-now")
        page.fill("input[name='email']")
    """
    patterns = [
        r'selector\s+["\']([^"\']+)["\']',
        r'locator\(["\']([^"\']+)["\']',
        r'\.click\(["\']([^"\']+)["\']',
        r'\.fill\(["\']([^"\']+)["\']',
        r'\.type\(["\']([^"\']+)["\']',
        r'get_by_role\(["\']([^"\']+)["\']',
        r'get_by_text\(["\']([^"\']+)["\']',
        r'Waiting for selector ["\']([^"\']+)["\']',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, error, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def get_ai_fix_with_semantic_context(
    code: str,
    error: str,
    screenshot: Optional[str] = None,
    project_root: Path = None,
    feedback_context: str = ""
) -> str:
    """
    Enhanced AI healing that enriches the error context with semantic
    selector alternatives from ChromaDB BEFORE calling the AI.
    
    This feeds the AI better information rather than appending
    useless comments to the fix output.
    """
    enriched_error = error
    
    # Check if selector-related and we have a project root
    if project_root:
        selector_keywords = ["Timeout", "not found", "no such element", "locator", "selector"]
        is_selector_error = any(kw.lower() in error.lower() for kw in selector_keywords)
        
        if is_selector_error:
            try:
                from kernhell.semantic_db import SemanticSelector
                
                failed_selector = _extract_selector_from_error(error)
                if failed_selector:
                    db = SemanticSelector(project_root)
                    alternatives = db.find_similar(failed_selector, n_results=5)
                    
                    if alternatives:
                        alt_text = ", ".join(alternatives)
                        enriched_error = (
                            f"{error}\n\n"
                            f"=== SEMANTIC SELECTOR ALTERNATIVES ===\n"
                            f"The following selectors on this page have similar meaning: {alt_text}\n"
                            f"Use one of these if the original selector is broken."
                        )
                        log_info(f"Enriched AI context with {len(alternatives)} selector alternatives")
            except ImportError:
                pass  # ChromaDB not installed, skip silently
            except Exception as e:
                log_warning(f"Semantic enrichment failed: {e}")
    
    return get_ai_fix(code, enriched_error, screenshot, feedback_context)
