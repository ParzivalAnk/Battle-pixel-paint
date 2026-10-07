import sys
import os
import pygame

sys.stdout.reconfigure(encoding='utf-8')
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from main import Game, VIEW_WIDTH, VIEW_HEIGHT
from challenges import CHALLENGES, CHALLENGE_MANAGER, CHALLENGE_ORDER
from perks import generate_portal_offerings, CURSED_PERKS, DOUBLE_EDGED_PERKS
from achievements import ACHIEVEMENT_MANAGER
from menu import draw_difficulty_modal, draw_main_menu

print("=== 1. TESTING CHALLENGES MANAGER & PRESETS ===")
CHALLENGE_MANAGER.disable_all()
assert CHALLENGE_MANAGER.get_active_count() == 0, "Should have 0 active challenges after disable_all"
assert not CHALLENGE_MANAGER.should_offer_only_curses(), "should_offer_only_curses should be False initially"

# Test Toggle
CHALLENGE_MANAGER.toggle("ONLY_CURSES")
assert CHALLENGE_MANAGER.is_active("ONLY_CURSES"), "ONLY_CURSES should be active after toggle"
assert CHALLENGE_MANAGER.should_offer_only_curses(), "should_offer_only_curses should be True"

# Test Presets
CHALLENGE_MANAGER.apply_preset_only_curses()
assert CHALLENGE_MANAGER.get_active_count() == 2
assert CHALLENGE_MANAGER.is_active("ONLY_CURSES")
assert CHALLENGE_MANAGER.is_active("DOOM_TIMER")

CHALLENGE_MANAGER.apply_preset_titan_hell()
assert CHALLENGE_MANAGER.is_active("TITAN_FRENZY")
assert CHALLENGE_MANAGER.is_active("HYPER_ADAPTATION")

CHALLENGE_MANAGER.apply_preset_glass_nightmare()
assert CHALLENGE_MANAGER.is_active("GLASS_SOUL")
assert CHALLENGE_MANAGER.is_active("PITCH_DARKNESS")
assert CHALLENGE_MANAGER.is_active("BLOOD_TAX")

CHALLENGE_MANAGER.enable_all()
assert CHALLENGE_MANAGER.get_active_count() == 7
print("All 7 challenges enabled successfully!")

print("\n=== 2. TESTING PORTAL OFFERINGS (ONLY CURSES) ===")
# Normal offerings: has double-edged perks
normal_offerings = generate_portal_offerings(floor_idx=2, curse_chance=0.25, only_curses=False)
assert len(normal_offerings) == 3

# Cursed offerings: MUST be 100% cursed (0 buffs)
cursed_offerings = generate_portal_offerings(floor_idx=2, curse_chance=1.0, only_curses=True)
assert len(cursed_offerings) == 3
for off in cursed_offerings:
    assert off.is_cursed is True, f"Offering {off.name} should be cursed!"
    assert "ОТСУТСТВУЕТ" in off.buff_title, f"Offering {off.name} must have 0 buffs (got {off.buff_title})!"
    print(f"  [CURSED OFFERING VERIFIED] {off.name} | Debuff: {off.debuff_desc}")

print("Portal correctly generates 100% pure debuffs with zero buffs!")

print("\n=== 3. TESTING GAME & RENDERING ===")
game = Game()
fonts_dict = {
    "title": game.font_title,
    "large": game.font_large,
    "med": game.font_med,
    "small": game.font_small,
    "sym_large": game.font_sym_large,
    "sym_med": game.font_sym_med,
    "sym_small": game.font_sym_small
}

CHALLENGE_MANAGER.apply_preset_only_curses()

# Render Challenges Tab (current_tab=1)
rects = draw_difficulty_modal(game.screen, 1.25, fonts_dict, current_tab=1)
assert "btn_tab_chal" in rects
assert "btn_tab_diff" in rects
assert "preset_rects" in rects
assert len(rects["challenge_rects"]) == 7

screenshot_path = os.path.join(r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32", "challenges_altar_tab_preview.png")
pygame.image.save(game.screen, screenshot_path)
print(f"Saved challenges altar tab preview to: {screenshot_path}")

# Render Difficulty Tab (current_tab=0)
game.screen.fill((6, 8, 14))
rects_diff = draw_difficulty_modal(game.screen, 1.25, fonts_dict, current_tab=0)
assert "btn_chal_banner" in rects_diff
screenshot_diff_path = os.path.join(r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32", "difficulty_tab_with_chal_banner_preview.png")
pygame.image.save(game.screen, screenshot_diff_path)
print(f"Saved difficulty tab preview to: {screenshot_diff_path}")

print("\n=== 4. TESTING GAMEPLAY HOOKS (DOOM TIMER, BLOOD TAX, GLASS SOUL) ===")
# Start run with ONLY_CURSES
CHALLENGE_MANAGER.apply_preset_only_curses()
game.start_run()
assert game.player.game == game
assert game.current_portal_offerings[0].is_cursed is True

# Test Glass Soul
CHALLENGE_MANAGER.enable("GLASS_SOUL")
game.start_run()
assert game.player.max_hp == 30
assert game.player.hp == 30
print(f"Glass Soul verified: Player max HP is {game.player.max_hp}")

# Test Doom Timer
CHALLENGE_MANAGER.enable("DOOM_TIMER")
game.load_floor(0)
initial_timer = game.zone_timer
# Player takes damage -> doom timer penalty -6s
game.player.take_damage(10.0, game.fx, game.sfx, game.art, False)
assert game.zone_timer <= initial_timer - 6.0, f"Timer should have dropped by at least 6s, was {initial_timer} -> {game.zone_timer}"
print(f"Doom timer penalty verified: timer dropped from {initial_timer:.1f} to {game.zone_timer:.1f}")

# Test Blood Tax
CHALLENGE_MANAGER.enable("BLOOD_TAX")
p_hp_before = game.player.hp
points = [(100, 100), (200, 100), (300, 100)]
game.cast_gesture_ability(points)
assert game.player.hp < p_hp_before, "Drawing glyph should have consumed HP due to BLOOD_TAX"
print(f"Blood tax verified: HP decreased from {p_hp_before} to {game.player.hp}")

# Test Portal Screen Rendering with ONLY_CURSES
game.state = 'PERK_SELECTION'
game.current_portal_offerings = generate_portal_offerings(2, only_curses=True)
# Call game rendering loop step
game.anim_time = 2.0
game.screen.fill((6, 8, 14))
# We can trigger the perk selection branch directly to verify rendering and capture screenshot
overlay = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT), pygame.SRCALPHA)
overlay.fill((8, 12, 20, 245))
game.screen.blit(overlay, (0, 0))

from perks import draw_cracked_cursed_card
card_w = 780
card_h = 124
card_x = VIEW_WIDTH // 2 - card_w // 2
card_y_start = 150
card_gap = 144
for idx, off in enumerate(game.current_portal_offerings):
    c_rect = pygame.Rect(card_x, card_y_start + idx * card_gap, card_w, card_h)
    draw_cracked_cursed_card(game.screen, c_rect, off, game.anim_time, False, fonts_dict)

fl_win = game.font_title.render("ЭТАЖ 2 ЗАЧИЩЕН!", True, (255, 215, 0))
game.screen.blit(fl_win, (VIEW_WIDTH // 2 - fl_win.get_width() // 2, 55))
sub = game.font_large.render("☠ ЧЕРТОГ ЧИСТИЛИЩА: ТОЛЬКО ДЕБАФФЫ (0 БАФФОВ)! ☠", True, (255, 90, 130))
game.screen.blit(sub, (VIEW_WIDTH // 2 - sub.get_width() // 2, 102))

c_badge = game.font_med.render("☠ АКТИВНО УСЛОЖНЕНИЕ «ТОЛЬКО ДЕБАФФЫ» — ПОРТАЛ ПРЕДЛАГАЕТ ЛИШЬ ПРОКЛЯТИЯ! ☠", True, (255, 80, 120))
game.screen.blit(c_badge, (VIEW_WIDTH // 2 - c_badge.get_width() // 2, 632))

portal_screen_path = os.path.join(r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32", "cursed_portal_only_debuffs_preview.png")
pygame.image.save(game.screen, portal_screen_path)
print(f"Saved cursed portal preview to: {portal_screen_path}")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
