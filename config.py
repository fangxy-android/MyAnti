"""Configuration manager for Codex-style Desktop Pet."""
import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "character": "sakura",
    "scale": 2.0,
    "always_on_top": True,
    "sound_enabled": True,
    "sound_volume": 0.7,
    "speech_bubble_duration": 4.5,
    "server_enabled": True,
    "server_port": 8765,
    "window_x": -1,
    "window_y": -1,
    "snap_to_bottom": False,
    "auto_sleep_minutes": 5,
    "theme": "dark",
    "monitor_system": True,
    "custom_skins_dir": ""
}

CONFIG_FILE = Path(__file__).resolve().parent / "config.json"

class Config:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"[Config] Error loading config: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

# Global singleton
cfg = Config()
