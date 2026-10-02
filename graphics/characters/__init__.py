"""Character registry for desktop pet."""
from graphics.characters.base import CharacterBase
from graphics.characters.dewey import DeweyCharacter
from graphics.characters.fireball import FireballCharacter
from graphics.characters.codebot import CodeBotCharacter
from graphics.characters.neko import NekoCharacter
from graphics.characters.slime import SlimeCharacter

REGISTRY: dict[str, CharacterBase] = {
    "dewey": DeweyCharacter(),
    "fireball": FireballCharacter(),
    "codebot": CodeBotCharacter(),
    "neko": NekoCharacter(),
    "slime": SlimeCharacter()
}

def get_character(name: str) -> CharacterBase:
    return REGISTRY.get(name.lower(), REGISTRY["dewey"])

def list_characters() -> list[dict]:
    return [
        {
            "id": char.name,
            "display_name": char.display_name,
            "description": char.description
        }
        for char in REGISTRY.values()
    ]
