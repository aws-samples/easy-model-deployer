import os
import json
import time
import requests
import packaging.version
from pathlib import Path
from emd.revision import VERSION
from rich.console import Console
from rich.panel import Panel
from typing import Optional, Dict, Any, Tuple
from emd.utils.logger_utils import get_logger

logger = get_logger(__name__)


class UpdateNotifier:
    def __init__(self):
        self.console = Console()
        self.cache_file = Path.home() / ".emd_update_cache.json"
        self.cache_duration = 3600  # 1 hour cache
        
    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        return VERSION == "0.0.0"
    
    def should_check_updates(self) -> bool:
        """Determine if we should check for updates"""
        # Skip in development mode
        if self.is_development_mode():
            return False
        
        # Skip if user disabled checks
        if os.getenv("EMD_DISABLE_UPDATE_CHECK", "").lower() in ["true", "1", "yes"]:
            return False
            
        return True
    
    def get_cached_version_info(self) -> Optional[Dict[str, Any]]:
        """Get cached version information"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data.get('timestamp', 0) < self.cache_duration:
                        return data
        except Exception as e:
            logger.debug(f"Failed to read update cache: {e}")
        return None
    
    def cache_version_info(self, latest_version: str, has_update: bool):
        """Cache version information"""
        try:
            data = {
                'latest_version': latest_version,
                'has_update': has_update,
                'timestamp': time.time(),
                'current_version': VERSION
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.debug(f"Failed to write update cache: {e}")
    
    def fetch_latest_version(self) -> Optional[str]:
        """Fetch latest version from PyPI"""
        try:
            response = requests.get(
                "https://pypi.org/pypi/easy-model-deployer/json", 
                timeout=2  # Quick timeout to avoid blocking
            )
            if response.status_code == 200:
                return response.json()["info"]["version"]
        except Exception as e:
            logger.debug(f"Failed to fetch latest version: {e}")
        return None
    
    def check_for_updates(self) -> Tuple[bool, Optional[str]]:
        """Check if updates are available with caching"""
        if not self.should_check_updates():
            return False, None
        
        # Try cache first
        cached = self.get_cached_version_info()
        if cached and cached.get('current_version') == VERSION:
            return cached['has_update'], cached.get('latest_version')
        
        # Fetch from PyPI
        latest = self.fetch_latest_version()
        if latest:
            try:
                has_update = packaging.version.parse(latest) > packaging.version.parse(VERSION)
                self.cache_version_info(latest, has_update)
                return has_update, latest
            except Exception as e:
                logger.debug(f"Failed to parse versions: {e}")
        
        return False, None
    
    def show_update_notification(self):
        """Display update notification if available"""
        try:
            has_update, latest_version = self.check_for_updates()
            
            if has_update and latest_version:
                # Display simple colored message
                self.console.print()  # Empty line for spacing
                self.console.print(f"📦 [bold blue]New version available![/bold blue] [dim]{VERSION}[/dim] → [bold green]{latest_version}[/bold green]")
                self.console.print(f"   [bold]Update:[/bold] pip install --upgrade easy-model-deployer")
                self.console.print()  # Empty line for spacing
        except Exception as e:
            # Silently fail to avoid disrupting command execution
            logger.debug(f"Failed to show update notification: {e}")


# Global instance
update_notifier = UpdateNotifier()