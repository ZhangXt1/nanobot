"""Desktop tool for controlling desktop applications."""

import platform
import subprocess
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool


class DesktopTool(Tool):
    """Tool to control desktop applications and media playback."""

    def __init__(self, workspace: Path | None = None):
        self._workspace = workspace
        self._platform = platform.system()

    @property
    def name(self) -> str:
        return "desktop"
    
    @property
    def description(self) -> str:
        return "Control desktop applications and media playback, such as playing music."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'play_music', 'open_app', 'close_app', 'list_apps'",
                    "enum": ["play_music", "open_app", "close_app", "list_apps"]
                },
                "target": {
                    "type": "string",
                    "description": "Target application or music file path (required for play_music and open_app)"
                },
                "args": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Additional arguments for opening applications"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, action: str, target: str | None = None, args: list[str] | None = None, **kwargs: Any) -> str:
        try:
            if action == "play_music":
                return await self._play_music(target)
            elif action == "open_app":
                return await self._open_app(target, args)
            elif action == "close_app":
                return await self._close_app(target)
            elif action == "list_apps":
                return await self._list_apps()
            else:
                return f"Error: Unknown action: {action}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _play_music(self, target: str | None) -> str:
        """Play music file or start music player."""
        if not target:
            return "Error: Target is required for play_music action"

        try:
            if self._platform == "Windows":
                # Use Windows default player
                subprocess.run(["start", "", target], shell=True, check=True)
                return f"Started playing music: {target}"
            elif self._platform == "Darwin":  # macOS
                # Use macOS default player
                subprocess.run(["open", target], check=True)
                return f"Started playing music: {target}"
            elif self._platform == "Linux":
                # Try common Linux players
                try:
                    subprocess.run(["xdg-open", target], check=True)
                    return f"Started playing music: {target}"
                except Exception:
                    # Fallback to vlc if available
                    try:
                        subprocess.run(["vlc", target], check=True)
                        return f"Started playing music with VLC: {target}"
                    except Exception:
                        return "Error: No music player found"
            else:
                return f"Error: Platform {self._platform} not supported"
        except Exception as e:
            return f"Error playing music: {str(e)}"

    async def _open_app(self, target: str | None, args: list[str] | None) -> str:
        """Open desktop application."""
        if not target:
            return "Error: Target is required for open_app action"

        try:
            if self._platform == "Windows":
                # Use Windows start command
                cmd = ["start", "", target]
                if args:
                    cmd.extend(args)
                subprocess.run(cmd, shell=True, check=True)
                return f"Opened application: {target}"
            elif self._platform == "Darwin":  # macOS
                # Use macOS open command
                cmd = ["open", target]
                if args:
                    cmd.extend(args)
                subprocess.run(cmd, check=True)
                return f"Opened application: {target}"
            elif self._platform == "Linux":
                # Use xdg-open
                cmd = ["xdg-open", target]
                if args:
                    cmd.extend(args)
                subprocess.run(cmd, check=True)
                return f"Opened application: {target}"
            else:
                return f"Error: Platform {self._platform} not supported"
        except Exception as e:
            return f"Error opening application: {str(e)}"

    async def _close_app(self, target: str | None) -> str:
        """Close desktop application."""
        if not target:
            return "Error: Target is required for close_app action"

        try:
            if self._platform == "Windows":
                # Use taskkill command
                subprocess.run(["taskkill", "/F", "/IM", target], check=True)
                return f"Closed application: {target}"
            elif self._platform == "Darwin":  # macOS
                # Use pkill command
                subprocess.run(["pkill", "-f", target], check=True)
                return f"Closed application: {target}"
            elif self._platform == "Linux":
                # Use pkill command
                subprocess.run(["pkill", "-f", target], check=True)
                return f"Closed application: {target}"
            else:
                return f"Error: Platform {self._platform} not supported"
        except Exception as e:
            return f"Error closing application: {str(e)}"

    async def _list_apps(self) -> str:
        """List running applications."""
        try:
            if self._platform == "Windows":
                # Use tasklist command
                result = subprocess.run(["tasklist"], capture_output=True, text=True, check=True)
                return f"Running applications on Windows:\n{result.stdout[:2000]}"
            elif self._platform == "Darwin":  # macOS
                # Use ps command
                result = subprocess.run(["ps", "-e", "-o", "comm="], capture_output=True, text=True, check=True)
                apps = set(result.stdout.strip().split('\n'))
                return f"Running applications on macOS:\n" + "\n".join(sorted(apps))
            elif self._platform == "Linux":
                # Use ps command
                result = subprocess.run(["ps", "-e", "-o", "comm="], capture_output=True, text=True, check=True)
                apps = set(result.stdout.strip().split('\n'))
                return f"Running applications on Linux:\n" + "\n".join(sorted(apps))
            else:
                return f"Error: Platform {self._platform} not supported"
        except Exception as e:
            return f"Error listing applications: {str(e)}"
