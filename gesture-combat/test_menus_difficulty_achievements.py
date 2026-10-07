"""
test_menus_difficulty_achievements.py - Verification script for Main Menu, Difficulty, and Achievements.
"""

import os
import sys
import pygame
import time

sys.stdout.reconfigure(encoding='utf-8')

# Headless / Dummy video driver
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from main import Game, MAP_WIDTH, MAP_HEIGHT, VIEW_WIDTH, VIEW_HEIGHT
from difficulty import DIFFICULTY_MANAGER, DIFFICULTIES, DIFFICULTY_ORDER
from achievements import ACHIEVEMENT_MANAGER, draw_achievements_screen
from menu import draw_main_menu, draw_difficulty_modal, update_menu_embers

ARTIFACTS_DIR = r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32"

def run_tests():
    print("=== TEST 1: Initializing Game ===")
    game = Game()
    assert game.state == 'MAIN_MENU', f"Expected state MAIN_MENU, got {game.state}"
    assert game.art.title_menu_bg is not None, "title_menu_bg was not loaded in ArtAssets"
    print(f"Game initialized in state: {game.state}")
    print(f"Title background size: {game.art.title_menu_bg.get_size()}")

    fonts_dict = {
        "title": game.font_title,
        "large": game.font_large,
        "med": game.font_med,
        "small": game.font_small,
        "sym_large": game.font_sym_large,
        "sym_med": game.font_sym_med,
        "sym_small": game.font_sym_small
    }

    print("\n=== TEST 2: Testing Main Menu Rendering ===")
    update_menu_embers(0.016, VIEW_WIDTH, VIEW_HEIGHT)
    menu_buttons = draw_main_menu(game.screen, 1.0, fonts_dict, bg_image=game.art.title_menu_bg)
    assert "START" in menu_buttons, "START button missing"
    assert "DIFFICULTY" in menu_buttons, "DIFFICULTY button missing"
    assert "ACHIEVEMENTS" in menu_buttons, "ACHIEVEMENTS button missing"
    assert "DOJO" in menu_buttons, "DOJO button missing"
    assert "CUSTOM_GLYPH" in menu_buttons, "CUSTOM_GLYPH button missing"
    assert "QUIT" in menu_buttons, "QUIT button missing"
    print("Menu buttons rendered correctly:", list(menu_buttons.keys()))

    menu_preview_path = os.path.join(ARTIFACTS_DIR, "main_menu_preview.png")
    pygame.image.save(game.screen, menu_preview_path)
    print(f"Saved Main Menu preview to: {menu_preview_path}")

    print("\n=== TEST 3: Testing Difficulty Manager and Levels ===")
    for key in DIFFICULTY_ORDER:
        d = DIFFICULTIES[key]
        DIFFICULTY_MANAGER.set_difficulty(key)
        assert DIFFICULTY_MANAGER.current_key == key
        print(f"Level: {d.name} ({d.badge}) | HP: {d.player_hp} | Timer: {d.floor_timer}s | Enemy Dmg: x{d.enemy_damage_mult} | Spam Threshold: {d.spam_threshold_normal}/{d.spam_threshold_boss} | Curse: {int(d.curse_chance*100)}%")

    # Test Difficulty Selection Modal rendering
    diff_rects = draw_difficulty_modal(game.screen, 1.0, fonts_dict)
    assert "card_rects" in diff_rects
    assert "btn_back" in diff_rects
    assert len(diff_rects["card_rects"]) == 4

    diff_preview_path = os.path.join(ARTIFACTS_DIR, "difficulty_select_preview.png")
    pygame.image.save(game.screen, diff_preview_path)
    print(f"Saved Difficulty Select preview to: {diff_preview_path}")

    print("\n=== TEST 4: Starting Run with INQUISITOR difficulty ===")
    DIFFICULTY_MANAGER.set_difficulty("INQUISITOR")
    game.start_run()
    assert game.state == 'PLAYING', f"Expected PLAYING, got {game.state}"
    assert game.player.max_hp == 80, f"Expected 80 HP for INQUISITOR, got {game.player.max_hp}"
    assert game.zone_timer == 120.0, f"Expected 120s timer for INQUISITOR, got {game.zone_timer}"
    print(f"Player HP: {game.player.hp}/{game.player.max_hp}")
    print(f"Floor Timer: {game.zone_timer:.1f}s")

    # Verify enemy stats under INQUISITOR
    enemy = game.enemies[0]
    expected_speed = enemy.data["speed"] * 1.15
    expected_dmg = enemy.data["damage"] * 1.35
    assert abs(enemy.speed - expected_speed) < 0.1, f"Enemy speed mismatch: {enemy.speed} vs {expected_speed}"
    assert abs(enemy.damage - expected_dmg) < 0.1, f"Enemy damage mismatch: {enemy.damage} vs {expected_dmg}"
    print("Enemy difficulty scaling verified!")

    print("\n=== TEST 5: Achievements System & Screen ===")
    # Unlock a few achievements for testing
    ACHIEVEMENT_MANAGER.unlock("first_glyph")
    ACHIEVEMENT_MANAGER.unlock("first_fusion")
    ACHIEVEMENT_MANAGER.unlock("boss_slayer")
    ACHIEVEMENT_MANAGER.unlock("ultra_combo_cast")

    unlocked, total, pct = ACHIEVEMENT_MANAGER.get_progress()
    print(f"Achievements progress: {unlocked}/{total} ({pct}%)")
    assert unlocked >= 4, f"Expected at least 4 unlocked, got {unlocked}"

    # Render Achievements screen
    ach_rects = draw_achievements_screen(game.screen, 1.0, fonts_dict, scroll_page=0)
    assert "btn_back" in ach_rects
    assert "btn_next" in ach_rects

    ach_preview_path = os.path.join(ARTIFACTS_DIR, "achievements_screen_preview.png")
    pygame.image.save(game.screen, ach_preview_path)
    print(f"Saved Achievements Screen preview to: {ach_preview_path}")

    print("\n=== TEST 6: Achievement Toast Popup Banner ===")
    ACHIEVEMENT_MANAGER.active_popup = ACHIEVEMENT_MANAGER.achievements["curse_pact"]
    ACHIEVEMENT_MANAGER.popup_timer = 3.5 # fully settled at y = 20

    # Render toast popup banner over a clean dark arena background
    game.screen.fill((14, 18, 28))
    ACHIEVEMENT_MANAGER.draw_active_popup(game.screen, 1.0, fonts_dict)
    popup_preview_path = os.path.join(ARTIFACTS_DIR, "achievement_popup_preview.png")
    pygame.image.save(game.screen, popup_preview_path)
    print(f"Saved Achievement Toast Popup preview to: {popup_preview_path}")

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
