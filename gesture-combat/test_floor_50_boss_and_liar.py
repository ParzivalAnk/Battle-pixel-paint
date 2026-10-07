"""
test_floor_50_boss_and_liar.py
Comprehensive automated test suite for Floor 50 Boss (Верховный Судия Истины),
Interactive Dialogue, Lie Detection, and Achievement «Врунишка».
"""

import os
import sys
import pygame

# Set dummy video driver for headless execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.stdout.reconfigure(encoding='utf-8')

from achievements import ACHIEVEMENT_MANAGER, Achievement
from bestiary import BESTIARY
import main
from main import Game, Player, Enemy, VIEW_WIDTH, VIEW_HEIGHT

def run_tests():
    print("=" * 60)
    print("TEST SUITE: FLOOR 50 BOSS & «ВРУНИШКА» ACHIEVEMENT")
    print("=" * 60)

    # 1. Bestiary check
    print("\n[1] Verifying Bestiary entry for 'judge_of_truth'...")
    assert "judge_of_truth" in BESTIARY, "judge_of_truth must exist in BESTIARY!"
    boss_info = BESTIARY["judge_of_truth"]
    print(f"  ✓ Boss Name: {boss_info['name']}")
    print(f"  ✓ HP: {boss_info['hp']}, Scale: {boss_info['scale']}, Damage: {boss_info['damage']}")
    assert boss_info["hp"] >= 1000, "Boss HP should be suitably colossal for Floor 50!"
    assert boss_info["scale"] >= 1.5, "Boss scale should be large!"

    # 2. Achievement registry check
    print("\n[2] Verifying 'liar_achievement' in Achievement Manager...")
    assert "liar_achievement" in ACHIEVEMENT_MANAGER.achievements, "liar_achievement must be registered!"
    liar_ach = ACHIEVEMENT_MANAGER.achievements["liar_achievement"]
    print(f"  ✓ Title: {liar_ach.title}")
    print(f"  ✓ Description: {liar_ach.desc}")
    print(f"  ✓ Tier: {liar_ach.tier}")
    print(f"  ✓ Icon: {liar_ach.icon}")
    assert liar_ach.title == "Врунишка", f"Expected title 'Врунишка', got '{liar_ach.title}'"

    # Reset liar achievement for clean test
    liar_ach.unlocked = False
    liar_ach.unlocked_at = None

    # 3. Game Initialization
    print("\n[3] Initializing Game instance and checking floor 50 data...")
    game = Game()
    assert game.player.total_damage_taken_run == 0.0, "Initial run damage must be 0!"
    assert game.player.total_hits_taken_run == 0, "Initial run hits must be 0!"

    # Check floor 50 data property
    game.current_floor_idx = 49
    f_data = game.current_floor_data
    assert f_data["floor"] == 50, f"Expected floor 50, got {f_data['floor']}"
    assert "judge_of_truth" in f_data["waves"][0], "judge_of_truth must be in Floor 50 wave!"
    print(f"  ✓ Floor 50 Name: {f_data['name']}")

    # 4. Jump to floor 50 & Dialogue Trigger
    print("\n[4] Triggering Floor 50 load and verifying Dialogue trigger...")
    game.load_floor(49)
    assert game.state == 'BOSS_DIALOGUE', f"Expected state 'BOSS_DIALOGUE', got '{game.state}'"
    assert game.dialogue_stage == 'QUESTION', f"Expected stage 'QUESTION', got '{game.dialogue_stage}'"
    boss_instance = next((e for e in game.enemies if e.id == "judge_of_truth"), None)
    assert boss_instance is not None, "judge_of_truth must be spawned in enemies!"
    print(f"  ✓ Boss successfully spawned at ({boss_instance.x}, {boss_instance.y})")
    print(f"  ✓ Game successfully entered 'BOSS_DIALOGUE' state!")

    # 5. Test Lie Detection Branch:
    # Player takes damage, then claims "Да, ни единой царапины!" -> LIAR!
    print("\n[5] Testing Lie Detection branch (Player took damage -> claims No Damage)...")
    game.player.take_damage(35.0, game.fx, game.sfx, game.art, False)
    assert game.player.total_damage_taken_run == 35.0, f"Expected 35.0 damage, got {game.player.total_damage_taken_run}"
    assert game.player.total_hits_taken_run == 1

    # Choose option 1 ("Да")
    game.handle_boss_dialogue_choice(1)
    assert game.dialogue_stage == 'ANSWER_LIED', f"Expected 'ANSWER_LIED', got '{game.dialogue_stage}'"
    assert liar_ach.unlocked == True, "Achievement 'liar_achievement' must be unlocked when lying!"
    assert getattr(boss_instance, 'enraged', False) == True, "Boss must become enraged when lied to!"
    print(f"  ✓ Detected lie correctly! Boss replied: {game.dialogue_result_title}")
    print(f"  ✓ «Врунишка» achievement unlocked: {liar_ach.unlocked}")
    print(f"  ✓ Boss enraged status: {boss_instance.enraged}")

    # Render Dialogue Screen with active popup & save preview
    fonts_dict = {
        "title": game.font_title,
        "large": game.font_large,
        "med": game.font_med,
        "small": game.font_small,
        "sym_large": game.font_sym_large,
        "sym_med": game.font_sym_med,
        "sym_small": game.font_sym_small
    }
    dlg_surf = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
    dlg_surf.fill((16, 20, 28))
    game.draw_boss_dialogue(dlg_surf, 1.25, fonts_dict)
    ACHIEVEMENT_MANAGER.update_popups(0.05)
    ACHIEVEMENT_MANAGER.draw_active_popup(dlg_surf, 1.25, fonts_dict)
    
    artifact_dir = r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32"
    dlg_preview_path = os.path.join(artifact_dir, "boss_50_dialogue_lied_preview.png")
    pygame.image.save(dlg_surf, dlg_preview_path)
    print(f"  ✓ Saved dialogue lied preview to: {dlg_preview_path}")

    # 6. Test Combat Transition
    print("\n[6] Testing transition from Dialogue to Combat...")
    game.close_boss_dialogue()
    assert game.state == 'PLAYING', f"Expected state 'PLAYING', got '{game.state}'"
    print(f"  ✓ Combat resumed successfully! State: {game.state}")

    # Render Combat screen with Grand Boss Health Bar & save preview
    combat_surf = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
    # Fake render world
    combat_surf.fill((18, 22, 32))
    main.draw_enemy_sprite(combat_surf, game.art, boss_instance, VIEW_WIDTH // 2, VIEW_HEIGHT // 2, 1.0, 0.0)
    # Draw enraged aura
    e_pulse = 0.5 + 0.5 * 0.8
    e_rad = boss_instance.radius + 18 + int(6 * e_pulse)
    pygame.draw.circle(combat_surf, (255, 45, 45), (VIEW_WIDTH // 2, VIEW_HEIGHT // 2), e_rad, 3)
    # Draw boss HUD
    b_bar_w = 660
    b_bar_h = 24
    bx = VIEW_WIDTH // 2 - b_bar_w // 2
    by = 64
    pygame.draw.rect(combat_surf, (15, 18, 28), (bx, by, b_bar_w, b_bar_h), border_radius=4)
    pygame.draw.rect(combat_surf, (255, 60, 60), (bx, by, b_bar_w, b_bar_h), border_radius=4)
    pygame.draw.rect(combat_surf, (255, 230, 100), (bx, by, b_bar_w, b_bar_h), 2, border_radius=4)
    sym_s = game.font_sym_med.render("⚖", True, (255, 220, 80))
    boss_txt = game.font_med.render(" ВЕРХОВНЫЙ СУДИЯ ИСТИНЫ [В ЯРОСТИ ОТ ЛЖИ: +25% SPD]  HP: 1500 / 1500 ", True, (255, 255, 255))
    tot_w = sym_s.get_width() * 2 + boss_txt.get_width()
    start_x = VIEW_WIDTH // 2 - tot_w // 2
    combat_surf.blit(sym_s, (start_x, by + 3))
    combat_surf.blit(boss_txt, (start_x + sym_s.get_width(), by + 3))
    combat_surf.blit(sym_s, (start_x + sym_s.get_width() + boss_txt.get_width(), by + 3))

    combat_preview_path = os.path.join(artifact_dir, "boss_50_combat_enraged_preview.png")
    pygame.image.save(combat_surf, combat_preview_path)
    print(f"  ✓ Saved combat preview to: {combat_preview_path}")

    # 7. Test Truth Branch:
    print("\n[7] Testing Truth branch (Player took damage -> admits damage)...")
    game.open_boss_dialogue()
    game.player.total_damage_taken_run = 50.0
    game.player.total_hits_taken_run = 2
    game.handle_boss_dialogue_choice(2)
    assert game.dialogue_stage == 'ANSWER_TRUTH', f"Expected 'ANSWER_TRUTH', got '{game.dialogue_stage}'"
    print(f"  ✓ Honest reply verified: {game.dialogue_result_title}")

    # 8. Test True No-Hit Branch:
    print("\n[8] Testing True No-Hit branch (Player took 0 damage -> answers No-Hit)...")
    game.open_boss_dialogue()
    game.player.total_damage_taken_run = 0.0
    game.player.total_hits_taken_run = 0
    game.handle_boss_dialogue_choice(1)
    assert game.dialogue_stage == 'ANSWER_NO_HIT', f"Expected 'ANSWER_NO_HIT', got '{game.dialogue_stage}'"
    print(f"  ✓ True No-Hit verified: {game.dialogue_result_title}")

    # 9. Test Achievements Menu rendering with «Врунишка» unlocked
    print("\n[9] Testing Achievements Menu rendering with «Врунишка» unlocked...")
    ach_surf = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
    ach_surf.fill((10, 12, 18))
    # «Врунишка» is on page 2 (item index 12 in list of 13)
    from achievements import draw_achievements_screen
    draw_achievements_screen(ach_surf, 1.0, fonts_dict, scroll_page=2)
    ach_menu_preview_path = os.path.join(artifact_dir, "achievements_menu_liar_unlocked.png")
    pygame.image.save(ach_surf, ach_menu_preview_path)
    print(f"  ✓ Saved achievements menu preview to: {ach_menu_preview_path}")

    # 10. Test Initial Question Dialog preview
    print("\n[10] Saving initial Question modal preview...")
    game.open_boss_dialogue()
    q_surf = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
    q_surf.fill((16, 20, 28))
    game.draw_boss_dialogue(q_surf, 0.5, fonts_dict)
    q_preview_path = os.path.join(artifact_dir, "boss_50_question_modal_preview.png")
    pygame.image.save(q_surf, q_preview_path)
    print(f"  ✓ Saved question modal preview to: {q_preview_path}")

    print("\n" + "=" * 60)
    print("ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY! (EXIT 0)")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
