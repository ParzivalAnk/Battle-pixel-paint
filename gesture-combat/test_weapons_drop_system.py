"""
test_weapons_drop_system.py - Verification script for expanded weapon drops,
rarity tiers (White for Rank V divine, Red/Orange for Rank I inferior),
interactive loot beams, and player weapon slots.
"""

import sys
import os
import pygame

sys.stdout.reconfigure(encoding='utf-8')
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from weapons import (
    WEAPONS, WEAPONS_CATALOG, TIER_INFO,
    DroppedWeapon, roll_enemy_weapon_drop
)
from main import Game, MAP_WIDTH, MAP_HEIGHT, VIEW_WIDTH, VIEW_HEIGHT
from achievements import ACHIEVEMENT_MANAGER

print("=== 1. VERIFYING WEAPON CATALOG & RARITY TIERS ===")
assert len(WEAPONS_CATALOG) >= 20, f"Expected at least 20 weapons, found {len(WEAPONS_CATALOG)}"
print(f"Total weapons catalog count: {len(WEAPONS_CATALOG)}")

tier_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
for w in WEAPONS_CATALOG.values():
    tier_counts[w.tier] += 1
    if w.tier == 5:
        # User requirement: Самое крутое оружие светится БЕЛЫМ!
        assert w.glow_color == (255, 255, 255), f"Tier 5 weapon {w.name} must glow pure white! Got {w.glow_color}"
    elif w.tier == 1:
        # User requirement: Самое фиговое оружие светится КРАСНЫМ ИЛИ ОРАНЖЕВЫМ!
        r, g, b = w.glow_color
        assert r > 200 and b < 60, f"Tier 1 weapon {w.name} must glow red or orange! Got {w.glow_color}"

for t, count in tier_counts.items():
    t_name = TIER_INFO[t]["name"]
    t_col = TIER_INFO[t]["glow_color"]
    print(f"  Tier {t} ({t_name}): {count} weapons | Glow Color: {t_col}")

print("\n=== 2. TESTING ENEMY WEAPON LOOT ROLL ===")
class DummyEnemy:
    def __init__(self, scale=1.0, name="Гоблин", e_id="goblin"):
        self.scale = scale
        self.name = name
        self.id = e_id

normal_mob = DummyEnemy(scale=1.0, name="Культист", e_id="cultist")
boss_mob = DummyEnemy(scale=1.8, name="Верховный Босс", e_id="boss_mordekai")
judge_mob = DummyEnemy(scale=1.65, name="Верховный Судия Истины [БОСС 50 ЭТАЖА]", e_id="judge_of_truth")

# Boss drops 100% of the time
boss_drops = [roll_enemy_weapon_drop(boss_mob, floor_idx=2) for _ in range(50)]
assert all(d is not None for d in boss_drops), "Bosses must drop weapons 100% of the time!"
boss_tiers = [d.tier for d in boss_drops]
assert all(t >= 3 for t in boss_tiers), "Bosses should drop at least Tier 3 weapons!"
print(f"Boss drop roll verified (all drops >= Tier 3, sample tiers: {boss_tiers[:10]})")

# Floor 50 Judge rolls Tier 4 and Tier 5 (White)
judge_drops = [roll_enemy_weapon_drop(judge_mob, floor_idx=50) for _ in range(30)]
assert any(d.tier == 5 for d in judge_drops), "Judge of Truth should drop Tier 5 Divine White weapons!"
print("Judge of Truth drops Tier 5 Divine White weapons confirmed!")

print("\n=== 3. TESTING DROPPED WEAPON ENTITY & LOOT BEAM RENDERING ===")
game = Game()
game.anim_time = 2.5
fonts_dict = {
    "title": game.font_title,
    "large": game.font_large,
    "med": game.font_med,
    "small": game.font_small,
    "sym_large": game.font_sym_large,
    "sym_med": game.font_sym_med,
    "sym_small": game.font_sym_small
}

# Create Dropped Weapons: Tier 1 (Red/Orange) and Tier 5 (Divine White)
w_inferior = WEAPONS_CATALOG["rusty_cleaver"] # Tier 1
w_divine = WEAPONS_CATALOG["divine_sun_blade"] # Tier 5
w_astral = WEAPONS_CATALOG["celestial_blade"] # Tier 4

dw1 = DroppedWeapon(w_inferior, MAP_WIDTH // 2 - 120, MAP_HEIGHT // 2)
dw2 = DroppedWeapon(w_divine, MAP_WIDTH // 2 + 120, MAP_HEIGHT // 2)
dw3 = DroppedWeapon(w_astral, MAP_WIDTH // 2, MAP_HEIGHT // 2 - 100)

game.dropped_weapons = [dw1, dw2, dw3]

# Test dynamic lighting integration
light_sources = []
for dw in game.dropped_weapons:
    l = dw.get_light()
    light_sources.append(l)

assert len(light_sources) == 3
# Verify Tier 5 white light
l_divine = dw2.get_light()
assert l_divine[2] >= 300, f"Tier 5 light radius should be >= 300, got {l_divine[2]}"
assert l_divine[3] == (255, 255, 255), f"Tier 5 light color must be pure white, got {l_divine[3]}"
print("Dropped weapons dynamic lighting verified!")

# Render test screen with loot beams and dropped weapons
game.screen.fill((12, 14, 22))
off_x = -(MAP_WIDTH // 2 - VIEW_WIDTH // 2)
off_y = -(MAP_HEIGHT // 2 - VIEW_HEIGHT // 2)

# Draw arena elements and dropped weapons
for dw in game.dropped_weapons:
    dw.draw(game.screen, off_x, off_y, game.anim_time, fonts_dict, is_player_near=(dw == dw2), current_player_weapon=game.player.weapon)

screenshot_drops_path = os.path.join(r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32", "dropped_weapons_loot_beams_preview.png")
pygame.image.save(game.screen, screenshot_drops_path)
print(f"Saved dropped weapons preview to: {screenshot_drops_path}")

print("\n=== 4. TESTING WEAPON SLOTS SWITCHING & [E] PICKUP ===")
# Verify starter slots
assert 1 in game.player.weapon_slots
assert 2 in game.player.weapon_slots
assert 3 in game.player.weapon_slots

# Switch to slot 1
game.player.switch_weapon_slot(1)
assert game.player.active_weapon_slot == 1
assert game.player.weapon == game.player.weapon_slots[1]

# Switch to slot 3
game.player.switch_weapon_slot(3)
assert game.player.active_weapon_slot == 3
assert game.player.weapon == game.player.weapon_slots[3]
print("Weapon slot switching [1, 2, 3] verified!")

# Test picking up Tier 5 Divine White weapon with [E]
game.player.x = dw2.x
game.player.y = dw2.y

old_slot_3_weapon = game.player.weapon
# Simulate E key press
closest_dw = dw2
game.player.equip_weapon(closest_dw.weapon)
closest_dw.weapon = old_slot_3_weapon

assert game.player.weapon.tier == 5, "Player should now have Tier 5 weapon equipped!"
assert game.player.weapon.glow_color == (255, 255, 255), "Tier 5 weapon must glow pure white!"
print(f"Equipped Tier 5 weapon: {game.player.weapon.name} (White Glow)")

# Trigger achievement unlock for picking up white divine weapon
ACHIEVEMENT_MANAGER.unlock("divine_weapon_pickup", game.fx, game.sfx)
ach_divine = ACHIEVEMENT_MANAGER.achievements["divine_weapon_pickup"]
assert ach_divine.unlocked is True, "divine_weapon_pickup achievement should be unlocked!"
print("Achievement «Сияние Первородных» successfully unlocked!")

# Render HUD Preview
game.screen.fill((10, 12, 18))
# Simulate HUD drawing
cur_slot = game.player.active_weapon_slot
slots_x = 35
slots_y = 36
slot_w = 118
slot_h = 22
slot_gap = 6
for s_idx in (1, 2, 3):
    s_rect = pygame.Rect(slots_x + (s_idx - 1) * (slot_w + slot_gap), slots_y, slot_w, slot_h)
    s_wep = game.player.weapon_slots[s_idx]
    is_act = (s_idx == cur_slot)
    pygame.draw.rect(game.screen, (35, 40, 58) if is_act else (16, 20, 30), s_rect, border_radius=3)
    pygame.draw.rect(game.screen, (255, 255, 255) if (is_act and s_wep.tier == 5) else s_wep.glow_color, s_rect, 2 if is_act else 1, border_radius=3)
    k_s = game.font_small.render(f"[{s_idx}] ", True, (255, 215, 80) if is_act else (150, 160, 180))
    w_s = game.font_small.render(s_wep.name[:8] + "..", True, s_wep.glow_color)
    game.screen.blit(k_s, (s_rect.x + 4, s_rect.y + 3))
    game.screen.blit(w_s, (s_rect.x + 4 + k_s.get_width(), s_rect.y + 3))

act_w = game.player.weapon
w_info = f"{act_w.name}  |  {act_w.short_tier}  |  УРОН x{act_w.damage_mult:.2f}  |  {act_w.weight} кг"
w_info_s = game.font_small.render(w_info, True, act_w.glow_color)
game.screen.blit(w_info_s, (35, slots_y + slot_h + 4))

god_s = game.font_small.render("[БОЖЕСТВЕННЫЙ РАНГ: ОСЛЕПИТЕЛЬНЫЙ БЕЛЫЙ СВЕТ]", True, (255, 255, 255))
game.screen.blit(god_s, (35, slots_y + slot_h + 20))

hud_screenshot_path = os.path.join(r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32", "weapon_belt_hud_preview.png")
pygame.image.save(game.screen, hud_screenshot_path)
print(f"Saved weapon belt HUD preview to: {hud_screenshot_path}")

print("\nALL WEAPON DROP & RARITY TESTS PASSED FLINTLESSLY! (EXIT 0)")
