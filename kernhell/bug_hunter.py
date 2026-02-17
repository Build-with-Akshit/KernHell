"""
Bug Hunter Agent - Log monitoring and auto-fix system.
Monitors server logs for errors and automatically analyzes/fixes them.
"""
import time
import re
import json
from pathlib import Path
from typing import List, Callable, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from kernhell.utils import log_info, log_success, log_warning, log_error
from kernhell.providers import generic_call
from kernhell.core.config import config


class LogMonitor(FileSystemEventHandler):
    """Monitor log files for errors and auto-fix"""
    
    def __init__(self, patterns: List[str], alert_callback: Callable = None, cooldown: int = 30):
        self.error_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.alert_callback = alert_callback
        self.file_positions: Dict[str, int] = {}  # Track read position per file
        self.cooldown = cooldown  # Seconds between alerts for same error
        self._recent_errors: Dict[str, float] = {}  # error_hash -> last_seen_time
    
    def on_modified(self, event: FileModifiedEvent):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only monitor .log files
        if file_path.suffix != '.log':
            return
        
        # Read new lines only
        new_lines = self._read_new_lines(file_path)
        
        # Check for errors
        for line in new_lines:
            for pattern in self.error_patterns:
                if pattern.search(line):
                    # Dedup: skip if same error seen within cooldown window
                    error_key = line.strip()[:120]
                    now = time.time()
                    if now - self._recent_errors.get(error_key, 0) < self.cooldown:
                        continue
                    self._recent_errors[error_key] = now
                    self._handle_error(file_path, line)
                    break  # One match per line is enough
    
    def _read_new_lines(self, file_path: Path) -> List[str]:
        """Read only new lines since last check (handles log rotation)"""
        try:
            file_size = file_path.stat().st_size
            last_pos = self.file_positions.get(str(file_path), 0)
            
            # Detect log rotation: file got smaller
            if file_size < last_pos:
                last_pos = 0
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_pos)
                new_lines = f.readlines()
                self.file_positions[str(file_path)] = f.tell()
                
                return new_lines
        except Exception as e:
            log_warning(f"Failed to read {file_path}: {e}")
            return []
    
    def _handle_error(self, file_path: Path, error_line: str):
        """AI analyzes error and suggests fix"""
        log_error(f"🚨 ERROR DETECTED in {file_path.name}")
        log_error(f"   {error_line.strip()}")
        
        # Get context (5 lines before and after)
        context = self._get_context(file_path, error_line)
        
        # Ask AI for analysis
        analysis = self._analyze_error(error_line, context)
        
        if analysis:
            log_info(f"🤖 AI Analysis: {analysis.get('cause', 'Unknown')}")
            log_success(f"💡 Suggested Fix: {analysis.get('fix', 'No fix suggested')}")
            
            # Send alert
            if self.alert_callback:
                self.alert_callback({
                    'file': str(file_path),
                    'error': error_line.strip(),
                    'analysis': analysis
                })
            
            # Auto-fix if high confidence
            confidence = analysis.get('confidence', 0)
            if confidence > 0.8:
                log_info(f"🔧 Confidence > 80% ({confidence:.0%}), attempting auto-fix...")
                # TODO: Implement auto-fix logic
    
    def _get_context(self, file_path: Path, error_line: str, context_lines: int = 5) -> str:
        """Get surrounding lines for context"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Find error line
            for i, line in enumerate(lines):
                if error_line.strip() in line:
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    return ''.join(lines[start:end])
            
            return error_line
        except Exception:
            return error_line
    
    def _analyze_error(self, error: str, context: str) -> Optional[Dict]:
        """Use AI to analyze error"""
        prompt = f"""Analyze this server error and provide a fix.

ERROR:
{error}

CONTEXT:
{context}

Respond in JSON format:
{{
    "cause": "Brief explanation of what caused this error",
    "fix": "Specific fix to apply",
    "confidence": 0.0-1.0,
    "severity": "low|medium|high|critical"
}}
"""
        
        try:
            provider = config.current_provider
            api_key = config.get_active_key()
            
            if not api_key:
                return None
            
            response = generic_call(
                provider, 
                api_key, 
                "You are a senior DevOps engineer specializing in error analysis.", 
                prompt
            )
            
            if response:
                # Strip markdown code fences if AI wraps JSON in them
                cleaned = response.strip()
                if cleaned.startswith('```json'):
                    cleaned = cleaned[7:]
                elif cleaned.startswith('```'):
                    cleaned = cleaned[3:]
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3]
                
                return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            log_warning("AI returned invalid JSON for error analysis")
        except Exception as e:
            log_warning(f"AI analysis failed: {e}")
        
        return None


# Alert Functions

def send_slack_alert(message: Dict):
    """Send alert to Slack"""
    try:
        from slack_sdk import WebClient
        import os
        
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            log_warning("SLACK_BOT_TOKEN not set, skipping Slack alert")
            return
        
        client = WebClient(token=token)
        
        # Format message
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 KernHell Bug Alert"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*File:*\n{message['file']}"},
                    {"type": "mrkdwn", "text": f"*Error:*\n{message['error'][:100]}"}
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Analysis:*\n{message['analysis'].get('cause', 'Unknown')}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Suggested Fix:*\n```{message['analysis'].get('fix', 'No fix')}```"}
            }
        ]
        
        client.chat_postMessage(
            channel=os.getenv("SLACK_CHANNEL", "#kernhell-alerts"),
            blocks=blocks
        )
        
        log_success("✅ Slack alert sent")
    except Exception as e:
        log_warning(f"Slack alert failed: {e}")


def send_whatsapp_alert(message: Dict):
    """Send alert via WhatsApp (Twilio)"""
    try:
        from twilio.rest import Client
        import os
        
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not sid or not token:
            log_warning("Twilio credentials not set, skipping WhatsApp alert")
            return
        
        client = Client(sid, token)
        
        # Format message
        text = f"""🚨 KernHell Alert

File: {message['file']}
Error: {message['error'][:100]}

Analysis: {message['analysis'].get('cause', 'Unknown')}

Fix: {message['analysis'].get('fix', 'No fix')[:200]}
"""
        
        client.messages.create(
            to=f"whatsapp:{os.getenv('ALERT_PHONE')}",
            from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
            body=text
        )
        
        log_success("✅ WhatsApp alert sent")
    except Exception as e:
        log_warning(f"WhatsApp alert failed: {e}")
