"""
The Healer Engine v2.
Orchestrates AI providers with:
- Screenshot-enhanced diagnosis (Vision AI)
- Key rotation + provider failover
- Optimized single-shot accuracy
"""
from kernhell.core.config import config
from kernhell.providers import get_provider_fn, get_model_name, supports_vision
from kernhell.utils import log_info, log_warning, log_error, console
from typing import Optional


def get_ai_fix(code_content: str, error_log: str, screenshot_b64: str = None, feedback_context: str = "") -> str:
    """
    Multi-Provider AI Fix Engine with Vision Support.
    Accepts optional feedback_context for retry loops.
    """
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
    """
    available_providers = config.get_all_providers_with_keys()
    
    if has_vision:
        # Priority: NVIDIA (Unified 90B) > Google (Gemini 2.0) > OpenRouter
        if "nvidia" in available_providers: return "nvidia"
        if "google" in available_providers: return "google"
        if "openrouter" in available_providers: return "openrouter"
    else:
        # Priority: Groq (Fastest) > Cloudflare > NVIDIA > Google
        if "groq" in available_providers: return "groq"
        if "cloudflare" in available_providers: return "cloudflare"
        if "nvidia" in available_providers: return "nvidia"
        if "google" in available_providers: return "google"
    
    return None
