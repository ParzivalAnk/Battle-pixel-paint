import os
import sys
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from main import Game, Player, Enemy
from perks import generate_portal_offerings, CURSED_PERKS, DOUBLE_EDGED_PERKS, draw_cracked_cursed_card, draw_double_edged_card

def run_tests():
    print("=== TEST 1: Initializing Game ===")
    game = Game()
    print("Game initialized successfully!")

    print("\n=== TEST 2: Spell Spam Adaptation & Temporary Immunity on Normal Enemy ===")
    en = Enemy(100, 100, "stone_sentry")
    initial_hp = en.hp

    # Hit 1: Full damage
    dmg1 = 40.0
    en.take_hit(dmg1, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="КРИО", player=game.player)
    hp_after_1 = en.hp
    dealt_1 = initial_hp - hp_after_1
    print(f"Hit 1 dealt: {dealt_1:.1f} (expected ~40.0)")
    assert math.isclose(dealt_1, 40.0, rel_tol=1e-2), f"Expected 40.0, got {dealt_1}"

    # Hit 2: -25% adaptation
    en.take_hit(dmg1, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="КРИО", player=game.player)
    hp_after_2 = en.hp
    dealt_2 = hp_after_1 - hp_after_2
    print(f"Hit 2 dealt: {dealt_2:.1f} (expected ~30.0)")
    assert math.isclose(dealt_2, 30.0, rel_tol=1e-2), f"Expected 30.0, got {dealt_2}"

    # Hit 3: -50% adaptation
    en.take_hit(dmg1, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="КРИО", player=game.player)
    hp_after_3 = en.hp
    dealt_3 = hp_after_2 - hp_after_3
    print(f"Hit 3 dealt: {dealt_3:.1f} (expected ~20.0)")
    assert math.isclose(dealt_3, 20.0, rel_tol=1e-2), f"Expected 20.0, got {dealt_3}"

    # Hit 4: Triggers Immunity!
    en.take_hit(dmg1, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="КРИО", player=game.player)
    hp_after_4 = en.hp
    dealt_4 = hp_after_3 - hp_after_4
    print(f"Hit 4 (Immunity Trigger) dealt: {dealt_4:.1f} (expected 0.0)")
    assert "КРИО" in en.spell_immunities, "Enemy should have КРИО immunity"
    assert en.spell_immunities["КРИО"] > 0, "Immunity timer should be active"

    # Hit 5: During active immunity -> 0 damage
    en.take_hit(dmg1, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="КРИО", player=game.player)
    hp_after_5 = en.hp
    dealt_5 = hp_after_4 - hp_after_5
    print(f"Hit 5 (During Immunity) dealt: {dealt_5:.1f} (expected 0.0)")
    assert math.isclose(dealt_5, 0.0, abs_tol=1e-3), f"Expected 0.0 damage during immunity, got {dealt_5}"

    # Hit with DIFFERENT spell (ИНФЕРНО) -> Full damage dealt!
    en.take_hit(dmg1, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="ИНФЕРНО", player=game.player)
    hp_after_different = en.hp
    dealt_diff = hp_after_5 - hp_after_different
    print(f"Hit with rotated element (ИНФЕРНО) dealt: {dealt_diff:.1f} (expected ~40.0)")
    assert math.isclose(dealt_diff, 40.0, rel_tol=1e-2), f"Expected 40.0 with rotated element, got {dealt_diff}"

    print("\n=== TEST 3: Boss Faster Adaptation (Threshold 3) ===")
    boss = Enemy(200, 200, "grand_inquisitor_malchor")
    boss_hp_init = boss.hp
    # Hit 1
    boss.take_hit(50.0, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="МОЛНИЯ", player=game.player)
    # Hit 2
    boss.take_hit(50.0, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="МОЛНИЯ", player=game.player)
    # Hit 3 -> Boss triggers immunity immediately on hit 3!
    boss.take_hit(50.0, 0, 0, 0.1, False, game.fx, game.sfx, spell_tag="МОЛНИЯ", player=game.player)
    print(f"Boss immunities: {boss.spell_immunities}")
    assert "МОЛНИЯ" in boss.spell_immunities, "Boss should have МОЛНИЯ immunity on 3rd hit"
    print("Boss adaptation threshold verified successfully!")

    print("\n=== TEST 4: Portal Offerings & Cursed Pacts ===")
    offerings = generate_portal_offerings(2)
    print(f"Generated 3 offerings: {[o.name for o in offerings]}")
    assert len(offerings) == 3, f"Expected 3 offerings, got {len(offerings)}"

    # Force a cursed perk test
    cursed_perk = CURSED_PERKS[0]
    print(f"Testing Cursed Perk: {cursed_perk.name}")
    assert cursed_perk.is_cursed is True, "Perk should be marked cursed"
    old_dmg_taken = game.player.damage_taken_mult
    old_curses = game.player.curse_count
    cursed_perk.apply(game.player, game)
    assert game.player.curse_count == old_curses + 1, "Curse count should increase"
    assert game.player.damage_taken_mult > old_dmg_taken, "Player damage taken should increase"
    print(f"Curse count: {game.player.curse_count}, damage taken mult: {game.player.damage_taken_mult}")

    print("\n=== TEST 5: Rendering Cursed & Double-Edged Cards to Screenshot ===")
    surf = pygame.Surface((1200, 800))
    surf.fill((8, 12, 20))

    fonts_dict = {
        "large": game.font_large,
        "med": game.font_med,
        "small": game.font_small,
        "sym_large": game.font_sym_large,
        "sym_med": game.font_sym_med,
        "sym_small": game.font_sym_small
    }

    # Render 1 cursed and 2 double-edged cards
    test_offerings = [DOUBLE_EDGED_PERKS[0], cursed_perk, DOUBLE_EDGED_PERKS[1]]
    for idx, off in enumerate(test_offerings):
        r = pygame.Rect(210, 160 + idx * 144, 780, 124)
        if off.is_cursed:
            draw_cracked_cursed_card(surf, r, off, 0.5, idx == 1, fonts_dict)
        else:
            draw_double_edged_card(surf, r, off, 0.5, False, fonts_dict)

    preview_path = r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32\portal_offerings_preview.png"
    pygame.image.save(surf, preview_path)
    print(f"Saved preview screenshot to: {preview_path}")

    print("\n=== TEST 6: Testing Enemy Hex Shield Immunity Render in Arena ===")
    # Add immune enemy to game
    immune_en = Enemy(600, 400, "stone_sentry")
    immune_en.spell_immunities["КРИО"] = 4.5
    game.enemies = [immune_en]
    game.state = 'PLAYING'
    game.anim_time = 1.2

    # Call enemy update and verify no exceptions
    immune_en.update(0.1, game.player, game.fx, game.sfx, game.art, False, game.obstacles)
    assert "КРИО" in immune_en.spell_immunities
    print(f"Immunity countdown updated: {immune_en.spell_immunities['КРИО']:.2f}s remaining")

    # Render one frame
    render_surf = pygame.Surface((1200, 800))
    ex, ey = 600, 400
    from art import draw_enemy_sprite
    draw_enemy_sprite(render_surf, game.art, immune_en, ex, ey, game.anim_time, 0.0)
    # Hex shield
    hex_r = immune_en.radius + 14 + int(3 * math.sin(game.anim_time * 8.0))
    pygame.draw.circle(render_surf, (220, 90, 255), (ex, ey), hex_r, 2)
    imm_tags = ", ".join(immune_en.spell_immunities.keys())
    imm_badge = game.font_small.render(f"[ИММУНИТЕТ: {imm_tags}]", True, (245, 100, 255))
    render_surf.blit(imm_badge, (ex - imm_badge.get_width() // 2, ey - immune_en.radius - 34))
    
    shield_preview = r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32\enemy_immunity_shield_preview.png"
    pygame.image.save(render_surf, shield_preview)
    print(f"Saved enemy immunity shield preview to: {shield_preview}")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
