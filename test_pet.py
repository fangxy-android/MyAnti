"""Automated test suite for Codex Desktop Pet."""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PySide6.QtWidgets import QApplication

def run_tests():
    app = QApplication.instance() or QApplication(sys.argv)
    print("Testing Codex Desktop Pet components...")

    # 1. Config Test
    from config import cfg
    assert cfg.get("character") is not None, "Config failed"
    print("✅ Config test passed.")

    # 2. State Machine Test
    from engine.pet_state import StateMachine, PetState
    sm = StateMachine(PetState.IDLE)
    assert sm.current_state == PetState.IDLE
    sm.set_state(PetState.WORKING)
    assert sm.current_state == PetState.WORKING
    sm.set_state(PetState.IDLE)
    print("✅ State Machine test passed.")

    # 3. Sound Synthesis Test
    from engine.sound import RetroSoundFX
    fx = RetroSoundFX()
    for name in ["click", "done", "error", "bubble", "notify", "tick"]:
        assert name in fx._cache, f"Sound {name} missing"
        assert len(fx._cache[name]) > 100, f"Sound {name} invalid"
    print("✅ Retro Sound Synthesizer test passed.")

    # 4. Character Frame Rendering Test
    from graphics.characters import REGISTRY
    all_states = [
        PetState.IDLE, PetState.THINKING, PetState.WORKING, PetState.DONE,
        PetState.ERROR, PetState.WAITING, PetState.CLICKED, PetState.SLEEP
    ]
    for char_id, char in REGISTRY.items():
        print(f"Testing character '{char_id}' ({char.display_name})...")
        for state in all_states:
            frames = char.get_frames(state, target_size=128)
            assert len(frames) > 0, f"No frames generated for {char_id} in state {state}"
            for f in frames:
                assert not f.isNull(), f"Null pixmap for {char_id} in state {state}"
                assert f.width() == 128 and f.height() == 128

    print("✅ All 5 Characters & 40 State Frame Sets verified successfully!")

    # 5. Animation Engine Test
    from engine.animation import AnimationEngine
    ae = AnimationEngine(sm)
    assert ae.pet_size > 0
    # Test switching to every registered character
    for cid in REGISTRY.keys():
        ae.set_character(cid)
        assert ae.current_character.name == cid, f"AnimationEngine failed switching to {cid}"
    print("✅ Animation Engine character switching test passed.")

    # 6. UI & Server Components Test
    from ui.pet_window import PetWindow
    from ui.tray_icon import TrayIcon
    from server.http_server import PetHttpServer
    from server.monitor import SystemMonitor

    pw = PetWindow(sm, ae)
    assert pw is not None
    assert pw.bubble is not None
    assert pw.quick_bar is not None

    # Test character switching on PetWindow
    for cid in REGISTRY.keys():
        pw._on_character_changed(cid, announce=False)
        assert ae.current_character.name == cid
        assert pw.quick_bar.char_tag.text().find(ae.current_character.display_name) >= 0

    # Test real actions on PetWindow
    pw._wake_pet()
    assert sm.current_state == PetState.IDLE
    pw._sleep_pet()
    assert sm.current_state == PetState.SLEEP
    pw._reset_position(announce=False)
    pw._handle_pet_click()

    # Test QuickBar UI updates
    pw.quick_bar.update_state_ui(PetState.WORKING)
    assert pw.quick_bar.status_chip.text() == "● 编码中"
    pw.quick_bar.update_character_ui("dewey")
    assert "Dewey" in pw.quick_bar.char_tag.text()

    tray = TrayIcon(pw)
    assert tray is not None

    server = PetHttpServer(sm, pw, port=8769)
    server.start()

    import urllib.request
    import json
    # Test character switch over HTTP
    req = urllib.request.Request("http://127.0.0.1:8769/api/character", data=b'{"character":"neko"}', headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=2.0) as resp:
        res = json.loads(resp.read().decode())
        assert res.get("character") == "neko"

    # Test action over HTTP
    req = urllib.request.Request("http://127.0.0.1:8769/api/action", data=b'{"action":"wake"}', headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=2.0) as resp:
        res = json.loads(resp.read().decode())
        assert res.get("action") == "wake"

    server.stop()
    cfg.set("character", "sakura")
    cfg.set("window_x", 1800)
    cfg.set("window_y", 900)
    print("✅ UI, Tray, QuickBar, and Server tests passed.")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! Ready for launch.")

if __name__ == "__main__":
    run_tests()
