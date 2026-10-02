"""Character registry for desktop pet."""
from graphics.characters.base import CharacterBase
from graphics.characters.dewey import DeweyCharacter
from graphics.characters.fireball import FireballCharacter
from graphics.characters.codebot import CodeBotCharacter
from graphics.characters.neko import NekoCharacter
from graphics.characters.slime import SlimeCharacter
from graphics.characters.sakura import SakuraCharacter

REGISTRY: dict[str, CharacterBase] = {
    "sakura": SakuraCharacter(),
    "dewey": DeweyCharacter(),
    "fireball": FireballCharacter(),
    "codebot": CodeBotCharacter(),
    "neko": NekoCharacter(),
    "slime": SlimeCharacter()
}

ALIASES: dict[str, str] = {
    "robot": "codebot",
    "bot": "codebot",
    "code": "codebot",
    "default": "codebot",
    "pet": "codebot"
}

def get_character(name: str = "codebot") -> CharacterBase:
    key = str(name).lower().strip()
    key = ALIASES.get(key, key)
    return REGISTRY.get(key, REGISTRY["codebot"])

def list_characters() -> list[dict]:
    char = REGISTRY["codebot"]
    return [
        {
            "id": char.name,
            "display_name": char.display_name,
            "description": char.description
        }
    ]

