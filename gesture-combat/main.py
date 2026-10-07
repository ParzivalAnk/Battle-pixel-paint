import sys
import math
import random
import pygame

from recognizer import evaluate_gesture, SKILL_INFO, add_template, Point, resample, scale_and_center, register_custom_glyph
from weapons import WEAPONS, WEAPONS_CATALOG, DroppedWeapon, roll_enemy_weapon_drop
from effects import EffectManager
from audio import SoundFX
from art import (
    ArtAssets, draw_player_character, draw_enemy_sprite,
    draw_obstacle, draw_grimoire_lectern, draw_portal
)
from abilities import (
    BlackHoleVortex, FireFissure, GlacialStasis, MeteorImpact,
    GlacialCometFusion, FirestormVortexFusion, ThunderMeteorFusion, BloodVortexFusion,
    CrossSlashAbility, PrismaticBarrierAbility, InfiniteBladeBarrageAbility, CustomStrikeAbility,
    DimensionalRiftFusion, HolyPrismaticNovaFusion,
    cast_chain_lightning, cast_blood_harvest
)
from bestiary import BESTIARY
from combos import COMBO_MATRIX, ELEMENTS, GLYPH_TO_ELEMENT, UltraFreezeCataclysm, GenericUltraComboSpell
from perks import generate_portal_offerings, draw_cracked_cursed_card, draw_double_edged_card
from difficulty import DIFFICULTY_MANAGER, DIFFICULTIES, DIFFICULTY_ORDER
from challenges import CHALLENGES, CHALLENGE_ORDER, CHALLENGE_MANAGER
from achievements import ACHIEVEMENT_MANAGER, draw_achievements_screen
from menu import draw_main_menu, draw_difficulty_modal, update_menu_embers

# Virtual Arena Bounds (Big map with camera scrolling)
MAP_WIDTH = 2200
MAP_HEIGHT = 1600
VIEW_WIDTH = 1200
VIEW_HEIGHT = 800
FPS = 60

# Colors
TEXT_WHITE = (240, 245, 255)
TEXT_GOLD = (255, 220, 60)
TEXT_RED = (255, 75, 75)
TEXT_CYAN = (80, 225, 255)
TEXT_PURPLE = (220, 120, 255)

MUTATORS = [
    {"name": "«Стабильная Зона»", "desc": "Нормальный эфир.", "color": (100, 230, 160), "timer_mult": 1.0, "inertia_mult": 1.0, "jitter": 0.0},
    {"name": "«Магнитные Аномалии»", "desc": "Помехи эфира курсора.", "color": (170, 110, 255), "timer_mult": 1.0, "inertia_mult": 1.0, "jitter": 4.5},
    {"name": "«Кислотная Буря»", "desc": "Таймер сгорает на 35% быстрее!", "color": (255, 185, 45), "timer_mult": 1.35, "inertia_mult": 1.0, "jitter": 0.0},
    {"name": "«Плотный Эфир»", "desc": "Тяжелая инерция тел и оружия.", "color": (90, 190, 255), "timer_mult": 1.0, "inertia_mult": 1.5, "jitter": 0.0}
]

# Wave compositions per floor
FLOOR_WAVES = [
    {
        "floor": 1,
        "name": "«Катакомбы Новичка»",
        "mutator_idx": 0,
        "waves": [
            ["cult_neophyte", "cult_neophyte", "stone_sentry"],
            ["cult_zealot", "blood_inquisitor", "ember_wisp"],
            ["crimson_executioner", "blood_inquisitor", "stone_sentry"]
        ]
    },
    {
        "floor": 2,
        "name": "«Зал Кровавой Инквизиции»",
        "mutator_idx": 1,
        "waves": [
            ["blood_inquisitor", "blood_inquisitor", "shadow_drinker"],
            ["cult_zealot", "cult_zealot", "possessed_monk", "bishop_of_agony"],
            ["grand_inquisitor_malchor", "blood_inquisitor", "crimson_executioner"]
        ]
    },
    {
        "floor": 3,
        "name": "«Чрево Колоссов»",
        "mutator_idx": 2,
        "waves": [
            ["magma_golem", "stone_sentry", "fissure_breaker"],
            ["obsidian_juggernaut", "quake_titan", "frost_shardling"],
            ["goliath_prime_titan", "magma_golem", "runic_automaton"]
        ]
    },
    {
        "floor": 4,
        "name": "«Некрополь Архилича»",
        "mutator_idx": 3,
        "waves": [
            ["plague_skeleton", "plague_skeleton", "bone_legionnaire"],
            ["crypt_wraith", "rot_bomber", "death_knight", "banshee_screamer"],
            ["archlich_mordecai", "death_knight", "lich_archivist"]
        ]
    },
    {
        "floor": 5,
        "name": "«Трон Первородного Хаоса»",
        "mutator_idx": 0,
        "waves": [
            ["void_stalker", "mind_flayer", "abyssal_burrower"],
            ["void_overlord", "gravity_oculus", "plasma_vortex_entity"],
            ["avatar_of_chaos", "goliath_prime_titan", "grand_inquisitor_malchor"]
        ]
    },
    {
        "floor": 6,
        "name": "«Арена Владычицы Клинков»",
        "mutator_idx": 1,
        "waves": [
            ["blood_inquisitor", "shadow_drinker", "crimson_executioner"],
            ["possessed_monk", "bishop_of_agony", "blood_inquisitor"],
            ["bladesovereign_valeria", "blood_inquisitor", "cult_zealot"]
        ]
    },
    {
        "floor": 7,
        "name": "«Бездна Левиафана»",
        "mutator_idx": 3,
        "waves": [
            ["void_stalker", "obsidian_juggernaut", "gravity_oculus"],
            ["void_overlord", "fissure_breaker", "rot_bomber"],
            ["abyssal_drakon_nadir", "void_overlord", "goliath_prime_titan"]
        ]
    }
]

class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 16
        diff = DIFFICULTY_MANAGER.current
        self.max_hp = diff.player_hp
        self.hp = diff.player_hp
        self.weapon_slots = {
            1: WEAPONS[1],
            2: WEAPONS[2],
            3: WEAPONS[3]
        }
        self.active_weapon_slot = 2
        self.weapon = self.weapon_slots[2]
        self.damage_taken_in_wave = False
        self.total_damage_taken_run = 0.0
        self.total_hits_taken_run = 0
        
        self.bonus_damage_mult = 1.0
        self.bonus_time_per_floor = 0.0
        self.speed_mult = 1.0
        self.damage_taken_mult = 1.0
        self.timer_drain_mult = 1.0
        self.bonus_jitter = 0.0
        self.lifesteal_per_kill = 0
        self.lifesteal_percent = 0.0
        self.freeze_duration_bonus = 0.0
        self.cataclysm_execute = False
        self.fusion_damage_bonus = 0.0
        self.curse_count = 0

        self.recovery_timer = 0.0
        self.fumble_timer = 0.0
        self.i_frame_timer = 0.0
        self.combo_count = 0
        self.combo_timer = 0.0
        self.alive = True
        self.aim_angle = 0.0

    def switch_weapon_slot(self, slot: int) -> bool:
        if slot in self.weapon_slots and self.weapon_slots[slot]:
            self.active_weapon_slot = slot
            self.weapon = self.weapon_slots[slot]
            return True
        return False

    def equip_weapon(self, new_weapon, slot=None):
        if slot is None:
            slot = self.active_weapon_slot
        old_weapon = self.weapon_slots.get(slot)
        self.weapon_slots[slot] = new_weapon
        if slot == self.active_weapon_slot:
            self.weapon = new_weapon
        return old_weapon

    def update(self, dt, keys, inertia_mult, obstacles):
        if self.recovery_timer > 0:
            self.recovery_timer = max(0.0, self.recovery_timer - dt)
        if self.fumble_timer > 0:
            self.fumble_timer = max(0.0, self.fumble_timer - dt)
        if self.i_frame_timer > 0:
            self.i_frame_timer = max(0.0, self.i_frame_timer - dt)

        if self.combo_timer > 0:
            self.combo_timer = max(0.0, self.combo_timer - dt)
            if self.combo_timer <= 0:
                self.combo_count = 0

        move_x = 0.0
        move_y = 0.0
        if self.fumble_timer <= 0:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                move_y -= 1.0
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                move_y += 1.0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_x -= 1.0
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_x += 1.0

        length = math.hypot(move_x, move_y)
        if length > 0:
            move_x /= length
            move_y /= length

        target_speed = 300.0 * self.weapon.speed_mult * getattr(self, 'speed_mult', 1.0)
        accel = 12.0 / (1.0 + (self.weapon.weight * 0.05 * inertia_mult))

        self.vx += (move_x * target_speed - self.vx) * accel * dt
        self.vy += (move_y * target_speed - self.vy) * accel * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Obstacle collision
        for obs in obstacles:
            dist = math.hypot(self.x - obs['x'], self.y - obs['y'])
            min_dist = self.radius + obs['radius']
            if dist < min_dist:
                overlap = min_dist - dist
                nx = (self.x - obs['x']) / max(dist, 0.001)
                ny = (self.y - obs['y']) / max(dist, 0.001)
                self.x += nx * overlap
                self.y += ny * overlap
                self.vx *= 0.5
                self.vy *= 0.5

        # Bounds
        pad = 60
        self.x = max(pad, min(MAP_WIDTH - pad, self.x))
        self.y = max(pad, min(MAP_HEIGHT - pad, self.y))

    def take_damage(self, amount, fx, sfx, art, is_shielded):
        if self.i_frame_timer > 0 or not self.alive:
            return
        if is_shielded:
            fx.spawn_sparks(self.x, self.y, (255, 230, 80), count=25, speed=260)
            fx.add_floating_text("БЛОКИРОВАНО! (БАСТИОН)", self.x, self.y - 35, TEXT_GOLD, size=24)
            sfx.play("parry")
            return

        effective_dmg = amount * getattr(self, 'damage_taken_mult', 1.0)
        self.hp = max(0, self.hp - effective_dmg)
        self.damage_taken_in_wave = True
        self.total_damage_taken_run += effective_dmg
        self.total_hits_taken_run += 1
        if getattr(self, 'game', None):
            CHALLENGE_MANAGER.on_player_damage_taken(self.game, effective_dmg)
        fx.add_screen_shake(14.0)
        fx.spawn_sparks(self.x, self.y, (255, 60, 60), count=18)
        art.add_blood_splatter(self.x, self.y, count=12)
        fx.add_floating_text(f"-{int(effective_dmg)} HP", self.x, self.y - 30, (255, 60, 60), size=26)
        sfx.play("hit")
        if self.hp <= 0:
            self.alive = False


class Enemy:
    def __init__(self, x, y, bestiary_id, hp_scale=1.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

        data = BESTIARY.get(bestiary_id, BESTIARY["stone_sentry"])
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.sprite_base = data["sprite_base"]
        self.tint = data["tint"]
        self.scale = data["scale"]
        self.radius = int(22 * self.scale)
        self.max_hp = int(data["hp"] * hp_scale)
        self.hp = self.max_hp
        diff = DIFFICULTY_MANAGER.current
        self.speed = data["speed"] * diff.enemy_speed_mult * CHALLENGE_MANAGER.get_enemy_speed_mult()
        self.damage = data["damage"] * diff.enemy_damage_mult * CHALLENGE_MANAGER.get_enemy_damage_mult()
        self.special = data["special"]
        self.alive = True

        self.attack_cooldown = random.uniform(1.2, 2.5)
        self.windup_timer = 0.0
        self.stun_timer = 0.0
        self.exhausted_timer = 0.0
        self.is_attacking = False
        self.is_frozen = False
        self.backstab_vulnerable = False
        self.combo_step = 0
        self.internal_clock = 0.0
        self.spell_hits = {}
        self.spell_immunities = {}

    def update(self, dt, player, fx, sfx, art, is_shielded, obstacles):
        if not self.alive:
            return

        self.internal_clock += dt
        if getattr(self, 'spell_immunities', None):
            expired = []
            for stag, rem in list(self.spell_immunities.items()):
                new_rem = rem - dt
                if new_rem <= 0:
                    expired.append(stag)
                else:
                    self.spell_immunities[stag] = new_rem
            for stag in expired:
                del self.spell_immunities[stag]
                fx.add_floating_text(f"ИММУНИТЕТ К [{stag}] ИСТЕК!", self.x, self.y - 45, (160, 255, 200), size=20)
                sfx.play("parry")

        if getattr(self, 'is_frozen', False):
            self.vx = 0.0
            self.vy = 0.0
            return

        if self.exhausted_timer > 0:
            self.exhausted_timer = max(0.0, self.exhausted_timer - dt)
            if random.random() < 0.25:
                fx.spawn_sparks(self.x, self.y, (255, 220, 80), count=2, speed=45)
            self.vx *= 0.82
            self.vy *= 0.82
            self.x += self.vx * dt
            self.y += self.vy * dt
            return

        if self.stun_timer > 0:
            self.stun_timer = max(0.0, self.stun_timer - dt)
            self.vx *= 0.88
            self.vy *= 0.88
            self.x += self.vx * dt
            self.y += self.vy * dt
            return

        self.vx *= 0.90
        self.vy *= 0.90
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Obstacle collision
        for obs in obstacles:
            dist = math.hypot(self.x - obs['x'], self.y - obs['y'])
            min_dist = self.radius + obs['radius']
            if dist < min_dist:
                overlap = min_dist - dist
                nx = (self.x - obs['x']) / max(dist, 0.001)
                ny = (self.y - obs['y']) / max(dist, 0.001)
                self.x += nx * overlap
                self.y += ny * overlap

        dist = math.hypot(player.x - self.x, player.y - self.y)
        dx = (player.x - self.x) / max(dist, 1.0)
        dy = (player.y - self.y) / max(dist, 1.0)

        # Multi-hit Boss Combo Sequences vs Regular Attacks
        is_boss = (self.scale > 1.35 or "БОСС" in self.name or "Титан" in self.name)
        if self.is_attacking:
            self.windup_timer += dt
            if random.random() < 0.35:
                fx.spawn_sparks(self.x, self.y, self.tint, count=3, speed=70)

            max_windup = 0.65 if is_boss else 0.85
            if self.windup_timer >= max_windup:
                self.windup_timer = 0.0
                reach = self.radius + player.radius + (50 if self.scale > 1.4 else 25)

                if is_boss:
                    self.combo_step += 1

                    # Unique Signature Combo Names per Boss!
                    if self.id == "grand_inquisitor_malchor":
                        combo_names = ["1/3: КРОВАВЫЙ ВЫПАД!", "2/3: ТРИБУНАЛ МУЧЕНИКА!", "3/3 ФИНИШЕР: БАГРОВАЯ КАЗНЬ!"]
                    elif self.id == "goliath_prime_titan":
                        combo_names = ["1/3: СЕЙСМИЧЕСКИЙ ТОПОТ!", "2/3: ТИТАНИЧЕСКИЙ ЗАМАХ!", "3/3 ФИНИШЕР: РАСКОЛ НЕБЕС!"]
                    elif self.id == "archlich_mordecai":
                        combo_names = ["1/3: ПРИЗЫВ ПРИЗРАКОВ!", "2/3: ЛЕДЯНАЯ ГРОБНИЦА!", "3/3 ФИНИШЕР: ЛУЧ СМЕРТИ!"]
                    elif self.id == "void_overlord":
                        combo_names = ["1/3: ТЕНЕВОЙ БЛИНК!", "2/3: ГРАВИТАЦИОННЫЙ РАЗРЫВ!", "3/3 ФИНИШЕР: СВЕРХНОВАЯ БЕЗДНЫ!"]
                    elif self.id == "avatar_of_chaos":
                        combo_names = ["1/3: ПЛАМЕННЫЙ ЗАЛП!", "2/3: ГРОЗОВОЙ РАЗРЯД!", "3/3 ФИНИШЕР: АПОКАЛИПСИС ХАОСА!"]
                    elif self.id == "bladesovereign_valeria":
                        combo_names = ["1/3: МГНОВЕННЫЙ ШАГ!", "2/3: ТАНЕЦ БАГРОВЫХ ЛЕЗВИЙ!", "3/3 ФИНИШЕР: ОМНИСЛЕШ: 1000 ПОРЕЗОВ!"]
                    elif self.id == "abyssal_drakon_nadir":
                        combo_names = ["1/3: ПРИЛИВ ТЬМЫ!", "2/3: ХВОСТОВОЙ СМЕТ!", "3/3 ФИНИШЕР: ДЫХАНИЕ СИНГУЛЯРНОСТИ!"]
                    elif self.id == "judge_of_truth":
                        combo_names = ["1/3: КАРА ЗА ЛОЖЬ!", "2/3: ВЕСЫ ПРАВОСУДИЯ!", "3/3 ФИНИШЕР: АБСОЛЮТНЫЙ ВЕРДИКТ!"]
                    else:
                        combo_names = [f"1/3: {self.name.split()[0]}!", "2/3: РАЗРЕЗ!", "3/3 ФИНИШЕР: СОКРУШЕНИЕ!"]

                    # Step 1: Initial Rush / Leap Strike
                    if self.combo_step == 1:
                        fx.add_floating_text(combo_names[0], self.x, self.y - 45, self.tint, size=24)
                        fx.add_screen_shake(14.0)
                        if self.id in ("grand_inquisitor_malchor", "bladesovereign_valeria"):
                            self.x += dx * 140 # Speed dash
                            self.y += dy * 140
                        if dist < reach + 40:
                            player.take_damage(self.damage * 0.80, fx, sfx, art, is_shielded)

                    # Step 2: Cleave / Flurry
                    elif self.combo_step == 2:
                        fx.add_floating_text(combo_names[1], self.x, self.y - 45, (255, 140, 40), size=24)
                        fx.add_screen_shake(18.0)
                        if dist < reach + 35:
                            player.take_damage(self.damage * 1.05, fx, sfx, art, is_shielded)

                    # Step 3: Obliteration Finisher!
                    elif self.combo_step >= 3:
                        fx.add_floating_text(combo_names[2], self.x, self.y - 50, TEXT_RED, size=28)
                        fx.add_screen_shake(28.0)
                        art.add_scorch_mark(self.x, self.y, radius=70)
                        if dist < reach + 65:
                            player.take_damage(self.damage * 1.65, fx, sfx, art, is_shielded)
                            player.vx += dx * 580
                            player.vy += dy * 580

                        self.is_attacking = False
                        self.combo_step = 0
                        self.exhausted_timer = CHALLENGE_MANAGER.get_boss_exhaustion_time(random.uniform(2.8, 3.8)) # Downtime window!
                        self.attack_cooldown = self.exhausted_timer + 0.8
                        fx.add_floating_text("БОСС ИСТОЩЕН! [ОКНО ДЛЯ КОНТРАТАКИ]", self.x, self.y - 65, TEXT_GOLD, size=24)
                else:
                    self.is_attacking = False
                    self.attack_cooldown = random.uniform(1.8, 2.8)
                    if dist < reach:
                        player.take_damage(self.damage, fx, sfx, art, is_shielded)
                        player.vx += dx * 280
                        player.vy += dy * 280
        else:
            self.attack_cooldown -= dt
            if dist > 55:
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt

            trigger = 90 if self.scale > 1.4 else 75
            if dist <= trigger and self.attack_cooldown <= 0:
                self.is_attacking = True
                self.windup_timer = 0.0

    def take_hit(self, damage, knockback_x, knockback_y, stun_sec, is_launcher, fx, sfx, spell_tag="АТАКА", player=None):
        if not self.alive:
            return

        # 1. Check active temporary immunity
        if hasattr(self, 'spell_immunities') and spell_tag in self.spell_immunities and self.spell_immunities[spell_tag] > 0:
            fx.spawn_sparks(self.x, self.y, (230, 110, 255), count=18, speed=220)
            rem = self.spell_immunities[spell_tag]
            fx.add_floating_text(f"★ ИММУНИТЕТ К [{spell_tag}]! [0 УРОНА, {rem:.1f}с]", self.x, self.y - 45, (245, 100, 255), size=26)
            sfx.play("parry")
            return

        # Rotated element hit achievement trigger:
        if getattr(self, 'spell_immunities', None) and len(self.spell_immunities) > 0 and spell_tag not in self.spell_immunities:
            ACHIEVEMENT_MANAGER.unlock("anti_spam_break", fx, sfx)

        # 2. Check hit frequency / spam adaptation (window: 6.5s)
        now = getattr(self, 'internal_clock', 0.0)
        if not hasattr(self, 'spell_hits'):
            self.spell_hits = {}
        if spell_tag not in self.spell_hits:
            self.spell_hits[spell_tag] = []

        self.spell_hits[spell_tag] = [t for t in self.spell_hits[spell_tag] if (now - t) < 6.5]
        self.spell_hits[spell_tag].append(now)
        hits_count = len(self.spell_hits[spell_tag])

        is_boss = (self.scale > 1.3 or "БОСС" in self.name or "Титан" in self.name or "Владычица" in self.name or "Инквизитор" in self.name)
        diff = DIFFICULTY_MANAGER.current
        norm_thr, boss_thr = CHALLENGE_MANAGER.get_spam_thresholds(diff.spam_threshold_normal, diff.spam_threshold_boss)
        immunity_threshold = boss_thr if is_boss else norm_thr

        if hits_count >= immunity_threshold:
            dur = 8.0 if CHALLENGE_MANAGER.is_active("HYPER_ADAPTATION") else (7.0 if is_boss else 5.0)
            if not hasattr(self, 'spell_immunities'):
                self.spell_immunities = {}
            self.spell_immunities[spell_tag] = dur
            self.spell_hits[spell_tag] = []
            fx.add_screen_shake(16.0)
            fx.spawn_sparks(self.x, self.y, (240, 90, 255), count=35, speed=320)
            fx.add_floating_text(f"★ ВРАГ ПОЛУЧИЛ ИММУНИТЕТ К [{spell_tag}] НА {int(dur)}с! [СПАМ]", self.x, self.y - 65, (255, 90, 255), size=26)
            sfx.play("crit")
            return
        elif hits_count == 2:
            damage *= 0.75
            fx.add_floating_text(f"ВРАГ ПРИВЫКАЕТ К [{spell_tag}]! (-25%)", self.x, self.y - 40, (255, 180, 80), size=22)
        elif hits_count == 3:
            damage *= 0.50
            fx.add_floating_text(f"АДАПТАЦИЯ К [{spell_tag}] (-50%)! [СПАМ]", self.x, self.y - 45, (255, 100, 100), size=24)

        if getattr(self, 'exhausted_timer', 0.0) > 0:
            damage *= 1.5
            fx.add_floating_text(f"★ УДАР ПО ИСТОЩЕНИЮ +50%! -{int(damage)}", self.x, self.y - 65, TEXT_GOLD, size=24)

        if self.backstab_vulnerable:
            damage *= 3.0
            self.backstab_vulnerable = False
            fx.add_floating_text(f"★ BACKSTAB CRIT x3! -{int(damage)}", self.x, self.y - 45, (255, 80, 240), size=28)
            fx.add_screen_shake(16.0)
            fx.spawn_sparks(self.x, self.y, (255, 100, 240), count=25, speed=260)
            sfx.play("crit")

        if player and getattr(player, 'cataclysm_execute', False) and spell_tag in ("КАТАКЛИЗМ", "ЗВЕЗДА"):
            if self.hp / max(1, self.max_hp) < 0.35:
                damage = self.hp + 999.0
                fx.add_floating_text("★ МГНОВЕННАЯ КАЗНЬ КАТАКЛИЗМА! ★", self.x, self.y - 75, (255, 50, 50), size=30)
                fx.add_screen_shake(24.0)

        self.hp = max(0, self.hp - damage)
        self.vx += knockback_x / (1.0 + self.scale * 0.5)
        self.vy += knockback_y / (1.0 + self.scale * 0.5)
        self.stun_timer = max(self.stun_timer, stun_sec)

        total_ls = getattr(player, 'lifesteal_percent', 0.0) + (getattr(player.weapon, 'lifesteal_bonus', 0.0) if player and getattr(player, 'weapon', None) else 0.0)
        if total_ls > 0 and damage > 0:
            heal = int(damage * total_ls)
            if heal > 0:
                player.hp = min(player.max_hp, player.hp + heal)
                if random.random() < 0.35:
                    fx.add_floating_text(f"+{heal} HP", player.x, player.y - 30, (80, 255, 140), size=20)

        if self.hp <= 0:
            self.alive = False
            self.is_frozen = False
            fx.spawn_sparks(self.x, self.y, (255, 70, 70), count=40, speed=260)
            sfx.play("crit")
            if is_boss:
                ACHIEVEMENT_MANAGER.unlock("boss_slayer", fx, sfx)
            if player and getattr(player, 'lifesteal_per_kill', 0) > 0:
                player.hp = min(player.max_hp, player.hp + player.lifesteal_per_kill)
                fx.add_floating_text(f"+{player.lifesteal_per_kill} HP (ЖНЕЦ)!", player.x, player.y - 45, (80, 255, 140), size=24)


class PentagramCataclysm:
    def __init__(self, x, y, damage_mult):
        self.x = float(x)
        self.y = float(y)
        self.duration = 1.8
        self.age = 0.0
        self.damage_mult = damage_mult
        self.alive = True
        self.has_detonated = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        self.age += dt
        if self.age >= 0.70 and not self.has_detonated:
            self.has_detonated = True
            fx.add_screen_shake(26.0)
            fx.spawn_sparks(self.x, self.y, (255, 60, 40), count=60, speed=400)
            art.add_scorch_mark(self.x, self.y, radius=85)
            sfx.play("crit")

            for en in enemies:
                if en.alive:
                    dist = math.hypot(en.x - self.x, en.y - self.y)
                    if dist < 320:
                        dmg = 175.0 * self.damage_mult
                        en.take_hit(dmg, (en.x - self.x) * 3.5, (en.y - self.y) * 3.5, 1.6, True, fx, sfx, spell_tag="КАТАКЛИЗМ", player=player)
                        art.add_blood_splatter(en.x, en.y, count=16)
                        fx.add_floating_text(f"★ КАТАКЛИЗМ! -{int(dmg)}", en.x, en.y - 45, (255, 60, 40), size=28)

        if self.age >= self.duration:
            self.alive = False

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        t = min(1.0, self.age / 0.70)
        radius = int(90 + 30 * t)
        
        star_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        pts = []
        rot = self.age * 3.0
        for i in range(5):
            a = rot + i * (2 * math.pi * 2 / 5)
            px = (radius + 5) + radius * math.cos(a)
            py = (radius + 5) + radius * math.sin(a)
            pts.append((px, py))
        
        alpha = int(220 * (1.0 - (self.age / self.duration)))
        if len(pts) >= 5:
            pygame.draw.polygon(star_surf, (255, 60, 40, alpha // 3), pts)
            pygame.draw.lines(star_surf, (255, 230, 80, alpha), True, pts, width=3)
            pygame.draw.circle(star_surf, (255, 120, 40, alpha), (radius + 5, radius + 5), radius, width=2)
        surface.blit(star_surf, (cx - (radius + 5), cy - (radius + 5)))

    def get_light(self):
        return (self.x, self.y, 280, (255, 80, 40), 0.95)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("GLYPH-BLADE: Giant Colossi & Compound Fusions")
        self.screen = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.art = ArtAssets(MAP_WIDTH, MAP_HEIGHT)
        self.fx = EffectManager()
        self.sfx = SoundFX()

        # States: 'MAIN_MENU', 'DIFFICULTY_SELECT', 'ACHIEVEMENTS_MENU', 'PLAYING', 'PAUSED', 'PERK_SELECTION', 'DOJO', 'TOME_OF_SYNTHESIS', 'BOSS_DIALOGUE'
        self.state = 'MAIN_MENU'
        self.achievements_page = 0
        self.menu_buttons = {}
        self.diff_modal_rects = {}
        self.ach_menu_rects = {}
        self.dialogue_rects = {}
        self.dialogue_stage = 'QUESTION'
        self.dialogue_choice = None
        self.dialogue_boss_name = "ВЕРХОВНЫЙ СУДИЯ ИСТИНЫ [БОСС 50 ЭТАЖА]"
        self.dialogue_boss_title = "Хранитель 50-го Эшелона • Владыка Весов Судеб"
        self.dialogue_question_lines = []
        self.dialogue_result_title = ""
        self.dialogue_result_lines = []
        self.dialogue_result_color = TEXT_GOLD
        self.dialogue_damage_reported = 0
        self.current_floor_idx = 0
        self.current_wave_idx = 0

        # Player & Entities
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.enemies = []
        self.active_abilities = []
        self.obstacles = []
        self.dropped_weapons = []
        self.lectern_pos = (MAP_WIDTH // 2 - 120, MAP_HEIGHT // 2)

        # Compound gesture memory for fusion!
        self.last_gesture_id = None
        self.last_gesture_time = 0.0

        # Bullet-Time Slo-Mo
        self.bullet_time_timer = 0.0

        # Camera
        self.cam_x = 0.0
        self.cam_y = 0.0

        # Run State
        diff = DIFFICULTY_MANAGER.current
        self.zone_timer = diff.floor_timer
        self.score = 0
        self.anim_time = 0.0
        self.is_drawing = False
        self.stroke_points = []
        self.last_accuracy_info = None
        self.highest_floor_cleared = 0

        # Multi-glyph combo chain in combat
        self.combo_gesture_chain = []

        # Combo Forge Menu State
        self.forge_slots = []
        self.forge_points = []
        self.forge_feedback = "Черти знаки по очереди в алтаре (минимум 3 знака)!"
        self.sealed_ultra_combo = None

        # Level exit portal
        self.portal_pos = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.portal_active = False
        self.current_portal_offerings = generate_portal_offerings(1, curse_chance=diff.curse_chance)

        # Custom Glyph Studio
        self.custom_points = []
        self.custom_glyph_recorded = False
        self.custom_glyph_feedback = "Зажми ЛКМ/ПКМ и нарисуй свой символ в золотом квадрате!"

        # Text Fonts (Arial renders Russian Cyrillic flawlessly on Windows)
        self.font_title = pygame.font.SysFont("arial", 32, bold=True)
        self.font_large = pygame.font.SysFont("arial", 22, bold=True)
        self.font_med = pygame.font.SysFont("arial", 16, bold=True)
        self.font_small = pygame.font.SysFont("arial", 13)

        # Symbol Fonts (Segoe UI Symbol renders Unicode glyphs ★ ❄ ⌛ 🛡 ⚛ ❂ flawlessly)
        self.font_sym_large = pygame.font.SysFont("segoe ui symbol", 26, bold=True)
        self.font_sym_med = pygame.font.SysFont("segoe ui symbol", 18, bold=True)
        self.font_sym_small = pygame.font.SysFont("segoe ui symbol", 14)

    def get_combo_forge_rects(self):
        """Returns geometry rectangles for all interactive elements in Combo Forge Menu."""
        btn_test = pygame.Rect(380, 615, 135, 38)
        btn_seal = pygame.Rect(525, 615, 150, 38)
        btn_clear = pygame.Rect(685, 615, 135, 38)
        btn_exit = pygame.Rect(380, 665, 440, 34)

        canvas_rect = pygame.Rect(380, 175, 440, 395)

        elem_rects = {}
        # 3 Area / Action types
        area_ids = ["AOE", "ZONE", "HP"]
        for idx, eid in enumerate(area_ids):
            elem_rects[eid] = pygame.Rect(35, 155 + idx * 30, 310, 26)

        # 9 Base elements (2 columns)
        base_ids = ["FIRE", "ICE", "LIGHTNING", "EARTH", "CHRONO", "STAR", "BLADE", "PRISM", "OMNI"]
        for idx, eid in enumerate(base_ids):
            col = idx % 2
            row = idx // 2
            elem_rects[eid] = pygame.Rect(35 + col * 158, 280 + row * 34, 152, 30)

        # 5 Secret elements (floors 1-5 unlocks)
        secret_ids = ["SUPERNOVA", "ABSOLUTE_ZERO", "CHRONO_SINGULARITY", "ANTIMATTER", "PRIMORDIAL_CHAOS"]
        for idx, eid in enumerate(secret_ids):
            elem_rects[eid] = pygame.Rect(35, 485 + idx * 36, 310, 32)

        return {
            "btn_test": btn_test,
            "btn_seal": btn_seal,
            "btn_clear": btn_clear,
            "btn_exit": btn_exit,
            "canvas_rect": canvas_rect,
            "elem_rects": elem_rects
        }

    def get_slot_element_info(self, item_key):
        """Maps any glyph or element identifier to its metadata dict."""
        if item_key in ELEMENTS:
            return ELEMENTS[item_key]
        elif item_key in GLYPH_TO_ELEMENT:
            return ELEMENTS[GLYPH_TO_ELEMENT[item_key]]
        return ELEMENTS["AOE"]

    def _draw_combo_forge_menu(self):
        """Renders the comprehensive 17-Element / 204-Combination Synthesis Forge."""
        overlay = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 18, 245))
        self.screen.blit(overlay, (0, 0))

        # Title & Subtitle with crisp font rendering
        star_l = self.font_sym_large.render("★ ", True, TEXT_GOLD)
        title_mid = self.font_title.render("КУЗНИЦА СВЯЗОК КОМБО (COMBO MATRIX FORGE)", True, TEXT_GOLD)
        star_r = self.font_sym_large.render(" ★", True, TEXT_GOLD)
        tot_tw = star_l.get_width() + title_mid.get_width() + star_r.get_width()
        tx = VIEW_WIDTH // 2 - tot_tw // 2
        self.screen.blit(star_l, (tx, 16))
        self.screen.blit(title_mid, (tx + star_l.get_width(), 16))
        self.screen.blit(star_r, (tx + star_l.get_width() + title_mid.get_width(), 16))

        sub = self.font_med.render(
            "Формула 204 комбо: 17 настроек x 3 знака (51) + 17 x 4 знака (68) + 17 x 5 знаков (85) = 204 комбинации!",
            True, (170, 200, 235)
        )
        self.screen.blit(sub, (VIEW_WIDTH // 2 - sub.get_width() // 2, 58))

        rects = self.get_combo_forge_rects()

        # =========================================================================
        # LEFT PANEL: 17 НАСТРОЕК И СТИХИЙ (17 SETTINGS)
        # =========================================================================
        lp_rect = pygame.Rect(25, 95, 330, 685)
        pygame.draw.rect(self.screen, (13, 17, 28), lp_rect)
        pygame.draw.rect(self.screen, (40, 56, 82), lp_rect, 2)

        lp_head = self.font_large.render("17 НАСТРОЕК И СТИХИЙ", True, TEXT_GOLD)
        self.screen.blit(lp_head, (lp_rect.centerx - lp_head.get_width() // 2, 105))

        # 3 Area Types
        g1_txt = self.font_small.render("● 3 ТИПА ДЕЙСТВИЯ (ОБЛАСТЬ / ЗОНА / HP):", True, TEXT_CYAN)
        self.screen.blit(g1_txt, (35, 134))

        area_keys = ["AOE", "ZONE", "HP"]
        for eid in area_keys:
            e_info = ELEMENTS[eid]
            r = rects["elem_rects"][eid]
            pygame.draw.rect(self.screen, (20, 26, 40), r)
            pygame.draw.rect(self.screen, e_info["color"], r, 1)

            sym_s = self.font_sym_med.render(f"[{e_info['symbol']}]", True, e_info["color"])
            self.screen.blit(sym_s, (r.x + 8, r.y + 2))

            name_s = self.font_small.render(e_info["name"], True, TEXT_WHITE)
            self.screen.blit(name_s, (r.x + 46, r.y + 5))

        # 9 Base Elements
        g2_txt = self.font_small.render("● 9 БАЗОВЫХ СТИХИЙ (КЛИКНИ ИЛИ НАРИСУЙ):", True, TEXT_CYAN)
        self.screen.blit(g2_txt, (35, 256))

        base_keys = ["FIRE", "ICE", "LIGHTNING", "EARTH", "CHRONO", "STAR", "BLADE", "PRISM", "OMNI"]
        for eid in base_keys:
            e_info = ELEMENTS[eid]
            r = rects["elem_rects"][eid]
            pygame.draw.rect(self.screen, (20, 26, 40), r)
            pygame.draw.rect(self.screen, e_info["color"], r, 1)

            sym_s = self.font_sym_med.render(f"[{e_info['symbol']}]", True, e_info["color"])
            self.screen.blit(sym_s, (r.x + 6, r.y + 4))

            short_name = e_info["name"].split()[0]
            name_s = self.font_small.render(short_name, True, TEXT_WHITE)
            self.screen.blit(name_s, (r.x + 40, r.y + 7))

        # 5 Secret Elements
        g3_txt = self.font_small.render("● 5 ЗАСЕКРЕЧЕННЫХ СТИХИЙ (ЭТАЖИ 1-5):", True, TEXT_CYAN)
        self.screen.blit(g3_txt, (35, 460))

        secret_keys = ["SUPERNOVA", "ABSOLUTE_ZERO", "CHRONO_SINGULARITY", "ANTIMATTER", "PRIMORDIAL_CHAOS"]
        for eid in secret_keys:
            e_info = ELEMENTS[eid]
            r = rects["elem_rects"][eid]
            is_open = COMBO_MATRIX.is_element_unlocked(eid)

            b_col = e_info["color"] if is_open else (50, 60, 80)
            pygame.draw.rect(self.screen, (18, 22, 34) if is_open else (12, 14, 20), r)
            pygame.draw.rect(self.screen, b_col, r, 1)

            sym_col = e_info["color"] if is_open else (100, 110, 130)
            sym_s = self.font_sym_med.render(f"[{e_info['symbol']}]", True, sym_col)
            self.screen.blit(sym_s, (r.x + 8, r.y + 5))

            name_col = TEXT_WHITE if is_open else (120, 130, 150)
            name_s = self.font_small.render(e_info["name"], True, name_col)
            self.screen.blit(name_s, (r.x + 46, r.y + 8))

            tag_str = "[ОТКРЫТО]" if is_open else f"[ЭТАЖ {e_info['floor_unlock']}]"
            tag_col = (80, 240, 140) if is_open else (240, 120, 60)
            tag_s = self.font_small.render(tag_str, True, tag_col)
            self.screen.blit(tag_s, (r.right - tag_s.get_width() - 8, r.y + 8))

        # =========================================================================
        # CENTER PANEL: SLOTS & DRAWING CANVAS
        # =========================================================================
        cp_rect = pygame.Rect(370, 95, 460, 685)
        pygame.draw.rect(self.screen, (14, 18, 30), cp_rect)
        pygame.draw.rect(self.screen, (45, 62, 92), cp_rect, 2)

        # 5 Combo Slots across top of center panel
        slot_w = 82
        slot_h = 56
        slot_y = 105
        for i in range(5):
            sx = 378 + i * 88
            sr = pygame.Rect(sx, slot_y, slot_w, slot_h)
            if i < len(self.forge_slots):
                item_key = self.forge_slots[i]
                e_data = self.get_slot_element_info(item_key)
                pygame.draw.rect(self.screen, (24, 32, 50), sr)
                pygame.draw.rect(self.screen, e_data["color"], sr, 2)

                s_surf = self.font_sym_large.render(f"{e_data['symbol']}", True, e_data["color"])
                self.screen.blit(s_surf, (sr.centerx - s_surf.get_width() // 2, sr.y + 3))

                sn_surf = self.font_small.render(e_data["name"], True, TEXT_WHITE)
                self.screen.blit(sn_surf, (sr.centerx - sn_surf.get_width() // 2, sr.y + 32))
            else:
                pygame.draw.rect(self.screen, (16, 20, 32), sr)
                pygame.draw.rect(self.screen, (40, 50, 70), sr, 1)
                req_txt = f"СЛОТ {i+1}" if i < 3 else f"+СЛОТ {i+1}"
                txt_col = (140, 155, 175) if i < 3 else (90, 105, 125)
                s_surf = self.font_small.render(req_txt, True, txt_col)
                self.screen.blit(s_surf, (sr.centerx - s_surf.get_width() // 2, sr.centery - s_surf.get_height() // 2))

        # Canvas Tablet
        canv_r = rects["canvas_rect"]
        pygame.draw.rect(self.screen, (10, 13, 22), canv_r)
        pygame.draw.rect(self.screen, (255, 215, 75), canv_r, 2)

        # Crosshair and runes in canvas
        pygame.draw.line(self.screen, (28, 38, 58), (canv_r.x, canv_r.centery), (canv_r.right, canv_r.centery), 1)
        pygame.draw.line(self.screen, (28, 38, 58), (canv_r.centerx, canv_r.y), (canv_r.centerx, canv_r.bottom), 1)
        pygame.draw.circle(self.screen, (34, 46, 70), (canv_r.centerx, canv_r.centery), 130, 1)

        # Watermark hint inside canvas if empty
        if len(self.forge_points) == 0:
            wm1 = self.font_med.render("РИСУЙ ЗНАКИ ПО ОЧЕРЕДИ НА ХОЛСТЕ", True, (60, 80, 115))
            wm2 = self.font_small.render("(Или просто кликай стихии слева)", True, (50, 70, 95))
            self.screen.blit(wm1, (canv_r.centerx - wm1.get_width() // 2, canv_r.centery - 20))
            self.screen.blit(wm2, (canv_r.centerx - wm2.get_width() // 2, canv_r.centery + 10))

        # Draw current stroke
        if len(self.forge_points) > 1:
            pygame.draw.lines(self.screen, (120, 240, 255), False, self.forge_points, 5)
            pygame.draw.lines(self.screen, (255, 255, 255), False, self.forge_points, 2)
            for pt in self.forge_points:
                pygame.draw.circle(self.screen, (140, 245, 255), pt, 4)

        # Feedback text
        fb_col = TEXT_GOLD if ("СИНТЕЗИРОВАНО" in self.forge_feedback or "ЗАПЕЧАТАНО" in self.forge_feedback) else TEXT_CYAN
        fb_s = self.font_small.render(self.forge_feedback, True, fb_col)
        self.screen.blit(fb_s, (cp_rect.centerx - fb_s.get_width() // 2, canv_r.bottom + 8))

        # Action Buttons
        # [ТЕСТ (SPACE)]
        b_test = rects["btn_test"]
        pygame.draw.rect(self.screen, (25, 38, 56), b_test)
        pygame.draw.rect(self.screen, (90, 180, 255), b_test, 1)
        bt_s = self.font_small.render("[ТЕСТ] (SPACE)", True, (160, 220, 255))
        self.screen.blit(bt_s, (b_test.centerx - bt_s.get_width() // 2, b_test.centery - bt_s.get_height() // 2))

        # [ЗАПЕЧАТАТЬ [F]]
        b_seal = rects["btn_seal"]
        pygame.draw.rect(self.screen, (40, 32, 20), b_seal)
        pygame.draw.rect(self.screen, TEXT_GOLD, b_seal, 2)
        star_icon = self.font_sym_small.render("★ ", True, TEXT_GOLD)
        seal_txt = self.font_small.render("ЗАПЕЧАТАТЬ [F]", True, TEXT_GOLD)
        tot_sw = star_icon.get_width() + seal_txt.get_width()
        self.screen.blit(star_icon, (b_seal.centerx - tot_sw // 2, b_seal.centery - seal_txt.get_height() // 2))
        self.screen.blit(seal_txt, (b_seal.centerx - tot_sw // 2 + star_icon.get_width(), b_seal.centery - seal_txt.get_height() // 2))

        # [ОЧИСТИТЬ]
        b_clear = rects["btn_clear"]
        pygame.draw.rect(self.screen, (34, 20, 24), b_clear)
        pygame.draw.rect(self.screen, (240, 80, 90), b_clear, 1)
        bc_s = self.font_small.render("ОЧИСТИТЬ (BS)", True, (255, 140, 150))
        self.screen.blit(bc_s, (b_clear.centerx - bc_s.get_width() // 2, b_clear.centery - bc_s.get_height() // 2))

        # [ВЫЙТИ В БОЙ]
        b_exit = rects["btn_exit"]
        pygame.draw.rect(self.screen, (18, 24, 38), b_exit)
        pygame.draw.rect(self.screen, (70, 95, 135), b_exit, 1)
        be_s = self.font_small.render("ЗАКРЫТЬ АЛТАРЬ И ВЕРНУТЬСЯ В БОЙ [ESC / C]", True, (190, 205, 230))
        self.screen.blit(be_s, (b_exit.centerx - be_s.get_width() // 2, b_exit.centery - be_s.get_height() // 2))

        # =========================================================================
        # RIGHT PANEL: RESULT CARD & CODEX
        # =========================================================================
        rp_rect = pygame.Rect(845, 95, 330, 685)
        pygame.draw.rect(self.screen, (13, 17, 28), rp_rect)
        pygame.draw.rect(self.screen, (40, 56, 82), rp_rect, 2)

        rp_head = self.font_large.render("РЕЗУЛЬТАТ СИНТЕЗА", True, TEXT_CYAN)
        self.screen.blit(rp_head, (rp_rect.centerx - rp_head.get_width() // 2, 105))

        if len(self.forge_slots) >= 3:
            res = COMBO_MATRIX.resolve_combo(self.forge_slots)
            
            res_card = pygame.Rect(858, 145, 304, 360)
            pygame.draw.rect(self.screen, (18, 24, 38), res_card)
            pygame.draw.rect(self.screen, res["color"], res_card, 2)

            # Name with icon rendered cleanly
            is_uf = ("Полярный" in res["name"] or "Заморозка" in res["name"])
            clean_name = res["name"].replace("❄ ", "").replace("★ ", "")
            head_icon = self.font_sym_med.render("❄ " if is_uf else "★ ", True, res["color"])
            self.screen.blit(head_icon, (res_card.x + 12, res_card.y + 12))
            avail_w = res_card.width - 24 - head_icon.get_width()
            r_font = self.font_med if self.font_med.size(clean_name)[0] <= avail_w else self.font_small
            r_name = r_font.render(clean_name, True, res["color"])
            self.screen.blit(r_name, (res_card.x + 12 + head_icon.get_width(), res_card.y + (12 if r_font == self.font_med else 15)))

            r_tier = self.font_small.render(f"РАНГ: {res['tier']} | УРОН x{res['mult']:.2f}", True, TEXT_GOLD)
            self.screen.blit(r_tier, (res_card.x + 12, res_card.y + 40))

            # Sequence badges drawn with symbol font
            seq_lbl = self.font_small.render("Связка: ", True, TEXT_WHITE)
            self.screen.blit(seq_lbl, (res_card.x + 12, res_card.y + 68))
            cur_x = res_card.x + 12 + seq_lbl.get_width()
            for idx_k, k in enumerate(self.forge_slots):
                e_data = self.get_slot_element_info(k)
                sym_s = self.font_sym_med.render(f"[{e_data['symbol']}]", True, e_data["color"])
                self.screen.blit(sym_s, (cur_x, res_card.y + 66))
                cur_x += sym_s.get_width() + 4
                if idx_k < len(self.forge_slots) - 1:
                    plus_s = self.font_small.render("+", True, (160, 180, 200))
                    self.screen.blit(plus_s, (cur_x, res_card.y + 68))
                    cur_x += plus_s.get_width() + 4

            if is_uf:
                uf_box = pygame.Rect(res_card.x + 10, res_card.y + 98, res_card.width - 20, 110)
                pygame.draw.rect(self.screen, (15, 35, 55), uf_box)
                pygame.draw.rect(self.screen, (140, 240, 255), uf_box, 2)

                uf_icon = self.font_sym_med.render("❄ ", True, (140, 240, 255))
                uf_t = self.font_med.render("УЛЬТРА-ЗАМОРОЗКА!", True, (140, 240, 255))
                tot_ufw = uf_icon.get_width() + uf_t.get_width()
                self.screen.blit(uf_icon, (uf_box.centerx - tot_ufw // 2, uf_box.y + 8))
                self.screen.blit(uf_t, (uf_box.centerx - tot_ufw // 2 + uf_icon.get_width(), uf_box.y + 8))
                
                uf_d1 = self.font_small.render("● Мгновенный абсолютный стазис", True, TEXT_WHITE)
                uf_d2 = self.font_small.render("  всех врагов и боссов на всей арене!", True, TEXT_WHITE)
                uf_d3 = self.font_small.render("● Крио-раскол с уроном x3.40+", True, (160, 230, 255))
                self.screen.blit(uf_d1, (uf_box.x + 10, uf_box.y + 36))
                self.screen.blit(uf_d2, (uf_box.x + 10, uf_box.y + 54))
                self.screen.blit(uf_d3, (uf_box.x + 10, uf_box.y + 76))
            else:
                desc_s1 = self.font_small.render(res["desc"][:42], True, (210, 220, 240))
                desc_s2 = self.font_small.render(res["desc"][42:85], True, (210, 220, 240))
                self.screen.blit(desc_s1, (res_card.x + 12, res_card.y + 105))
                self.screen.blit(desc_s2, (res_card.x + 12, res_card.y + 125))

            seal_h = self.font_small.render("Нажми [ENTER], чтобы привязать к [F]!", True, TEXT_GOLD)
            self.screen.blit(seal_h, (res_card.x + 12, res_card.bottom - 32))

        else:
            info_box = pygame.Rect(858, 145, 304, 360)
            pygame.draw.rect(self.screen, (16, 21, 33), info_box)
            pygame.draw.rect(self.screen, (45, 60, 85), info_box, 1)

            i1 = self.font_med.render("КАК СИНТЕЗИРОВАТЬ:", True, TEXT_GOLD)
            self.screen.blit(i1, (info_box.x + 12, info_box.y + 12))

            lines = [
                ("1.", "Начерти на холсте или кликни"),
                ("  ", "минимум 3 знака связки (до 5)."),
                ("2.", "Пример Легендарного Комбо:"),
                ("  ", "★ Звезда [★]"),
                ("  ", "+ Инферно [^]"),
                ("  ", "+ Крио [V]"),
                ("=>", "УЛЬТРА-ЗАМОРОЗКА!"),
                ("3.", "Жми [ENTER], чтобы запечатать"),
                ("  ", "в клавишу быстрого вызова [F]!")
            ]
            iy = info_box.y + 42
            for prefix, text in lines:
                c = (140, 240, 255) if "УЛЬТРА" in text or "Звезда" in text or "Инферно" in text or "Крио" in text else (210, 220, 240)
                if prefix in ("1.", "2.", "3.", "=>"):
                    s = self.font_small.render(f"{prefix} {text}", True, TEXT_GOLD if prefix != "=>" else (140, 240, 255))
                else:
                    s = self.font_small.render(f"   {text}", True, c)
                self.screen.blit(s, (info_box.x + 10, iy))
                iy += 26

        # Bottom section: Current Sealed Combo Status
        bot_box = pygame.Rect(858, 520, 304, 240)
        pygame.draw.rect(self.screen, (18, 22, 34), bot_box)
        pygame.draw.rect(self.screen, (55, 75, 110), bot_box, 1)

        b_title = self.font_med.render("БЫСТРЫЙ ВЫЗОВ В БОЮ [F]:", True, TEXT_GOLD)
        self.screen.blit(b_title, (bot_box.x + 12, bot_box.y + 12))

        if self.sealed_ultra_combo:
            sc = self.sealed_ultra_combo
            sc_s1 = self.font_small.render("АКТИВНОЕ ЗАПЕЧАТАННОЕ КОМБО:", True, TEXT_CYAN)
            self.screen.blit(sc_s1, (bot_box.x + 12, bot_box.y + 40))
            clean_sc_name = sc["name"].replace("❄ ", "").replace("★ ", "")
            sc_icon = self.font_sym_med.render("❄ " if "Полярный" in sc["name"] else "★ ", True, sc["color"])
            sc_s2 = self.font_med.render(clean_sc_name[:24], True, sc["color"])
            self.screen.blit(sc_icon, (bot_box.x + 12, bot_box.y + 64))
            self.screen.blit(sc_s2, (bot_box.x + 12 + sc_icon.get_width(), bot_box.y + 64))
            sc_s3 = self.font_small.render(f"Урон: x{sc['mult']:.2f} | В бою жми [F]!", True, (80, 240, 140))
            self.screen.blit(sc_s3, (bot_box.x + 12, bot_box.y + 92))
        else:
            sc_empty = self.font_small.render("Слот [F] пуст.", True, (140, 150, 170))
            self.screen.blit(sc_empty, (bot_box.x + 12, bot_box.y + 40))
            sc_hint = self.font_small.render("Собери 3+ знака и нажми [ENTER],", True, (170, 185, 205))
            sc_hint2 = self.font_small.render("чтобы зарядить клавишу [F]!", True, (170, 185, 205))
            self.screen.blit(sc_hint, (bot_box.x + 12, bot_box.y + 64))
            self.screen.blit(sc_hint2, (bot_box.x + 12, bot_box.y + 84))

        # 204 combinations formula badge
        f_box = pygame.Rect(bot_box.x + 10, bot_box.y + 125, bot_box.width - 20, 100)
        pygame.draw.rect(self.screen, (12, 16, 26), f_box)
        pygame.draw.rect(self.screen, (35, 50, 75), f_box, 1)

        f_head = self.font_small.render("БИБЛИОТЕКА КОМБО (204 ВСЕГО):", True, TEXT_GOLD)
        self.screen.blit(f_head, (f_box.x + 8, f_box.y + 6))
        f_l1 = self.font_small.render("● 17 x 3 знака = 51 комбо", True, (180, 195, 220))
        f_l2 = self.font_small.render("● 17 x 4 знака = 68 комбо", True, (180, 195, 220))
        f_l3 = self.font_small.render("● 17 x 5 знаков = 85 комбо", True, (180, 195, 220))
        f_sum = self.font_small.render("ИТОГО: 204 УНИКАЛЬНЫХ ЗАКЛИНАНИЯ", True, (80, 235, 255))
        self.screen.blit(f_l1, (f_box.x + 8, f_box.y + 26))
        self.screen.blit(f_l2, (f_box.x + 8, f_box.y + 44))
        self.screen.blit(f_l3, (f_box.x + 8, f_box.y + 62))
        self.screen.blit(f_sum, (f_box.x + 8, f_box.y + 80))

        self._generate_map_obstacles()
        self.load_floor(0)

    def _generate_map_obstacles(self):
        """Generates stone pillars, braziers, and altars across the huge map."""
        self.obstacles.clear()
        # Ring of Ancient Pillars
        for a in range(8):
            ang = a * (math.pi / 4)
            dist = 520
            px = MAP_WIDTH // 2 + dist * math.cos(ang)
            py = MAP_HEIGHT // 2 + dist * math.sin(ang)
            self.obstacles.append({'x': px, 'y': py, 'radius': 32, 'type': 'PILLAR'})

        # Outer room corner columns
        corners = [(350, 300), (MAP_WIDTH - 350, 300), (350, MAP_HEIGHT - 300), (MAP_WIDTH - 350, MAP_HEIGHT - 300)]
        for cx, cy in corners:
            self.obstacles.append({'x': cx, 'y': cy, 'radius': 40, 'type': 'PILLAR'})

        # Burning Braziers
        braziers = [
            (MAP_WIDTH // 2 - 250, MAP_HEIGHT // 2 - 200),
            (MAP_WIDTH // 2 + 250, MAP_HEIGHT // 2 - 200),
            (MAP_WIDTH // 2 - 250, MAP_HEIGHT // 2 + 200),
            (MAP_WIDTH // 2 + 250, MAP_HEIGHT // 2 + 200)
        ]
        for bx, by in braziers:
            self.obstacles.append({'x': bx, 'y': by, 'radius': 22, 'type': 'BRAZIER'})

    @property
    def current_floor_data(self):
        if self.current_floor_idx < len(FLOOR_WAVES):
            return FLOOR_WAVES[self.current_floor_idx]
        elif self.current_floor_idx == 49: # Floor 50!
            return {
                "floor": 50,
                "name": "«Чертог Истины: 50-й Уровень»",
                "mutator_idx": 1,
                "waves": [
                    ["judge_of_truth"]
                ]
            }
        return {
            "floor": self.current_floor_idx + 1,
            "name": f"«Бесконечная Бездна: Этаж {self.current_floor_idx + 1}»",
            "mutator_idx": self.current_floor_idx % len(MUTATORS),
            "waves": [
                ["void_overlord", "goliath_prime_titan"],
                ["avatar_of_chaos", "archlich_mordecai", "grand_inquisitor_malchor"]
            ]
        }

    @property
    def current_mutator(self):
        m_idx = self.current_floor_data.get("mutator_idx", 0)
        return MUTATORS[m_idx % len(MUTATORS)]

    def load_floor(self, floor_idx):
        self.current_floor_idx = floor_idx
        self.current_wave_idx = 0
        self.player.x = MAP_WIDTH // 2
        self.player.y = MAP_HEIGHT // 2 + 250
        self.player.vx = 0.0
        self.player.vy = 0.0

        self.enemies.clear()
        self.active_abilities.clear()
        self.dropped_weapons.clear()
        self.portal_active = False
        self.highest_floor_cleared = max(self.highest_floor_cleared, floor_idx)
        COMBO_MATRIX.update_floor_unlocks(self.highest_floor_cleared)
        diff = DIFFICULTY_MANAGER.current
        base_timer = 75.0 if CHALLENGE_MANAGER.is_active("DOOM_TIMER") else diff.floor_timer
        self.zone_timer = base_timer + self.player.bonus_time_per_floor
        self.bullet_time_timer = 0.0

        if floor_idx >= 1 and CHALLENGE_MANAGER.should_offer_only_curses():
            ACHIEVEMENT_MANAGER.unlock("cursed_survivor", self.fx, self.sfx)
        if floor_idx >= 1 and CHALLENGE_MANAGER.get_active_count() >= 3:
            ACHIEVEMENT_MANAGER.unlock("purgatory_conqueror", self.fx, self.sfx)
        if floor_idx >= 2:
            ACHIEVEMENT_MANAGER.unlock("floor_3_cleared", self.fx, self.sfx)
        if floor_idx >= 1 and DIFFICULTY_MANAGER.current_key in ("INQUISITOR", "NIGHTMARE"):
            ACHIEVEMENT_MANAGER.unlock("hardcore_victor", self.fx, self.sfx)
        if COMBO_MATRIX.is_element_unlocked("PRIMORDIAL_CHAOS"):
            ACHIEVEMENT_MANAGER.unlock("secret_archivist", self.fx, self.sfx)

        self.spawn_wave(0)

        # Trigger Floor 50 Boss Encounter Dialogue!
        if self.current_floor_data.get("floor") == 50:
            self.open_boss_dialogue()

    def spawn_wave(self, wave_idx):
        self.current_wave_idx = wave_idx
        self.player.damage_taken_in_wave = False
        f_data = self.current_floor_data
        wave_list = f_data["waves"][wave_idx]

        if wave_idx > 0:
            self.zone_timer += 35.0
            self.fx.add_floating_text("+35s ТАЙМЕР ЗА ВОЛНУ!", self.player.x, self.player.y - 110, TEXT_CYAN, size=24)

        hp_scale = 1.0 + (self.current_floor_idx * 0.15) + (wave_idx * 0.10)
        for b_id in wave_list:
            if b_id == "judge_of_truth":
                ex = MAP_WIDTH // 2
                ey = MAP_HEIGHT // 2 - 140
            else:
                ang = random.uniform(0, 2 * math.pi)
                dist = random.uniform(380, 680)
                ex = MAP_WIDTH // 2 + dist * math.cos(ang)
                ey = MAP_HEIGHT // 2 + dist * math.sin(ang)
            self.enemies.append(Enemy(ex, ey, b_id, hp_scale=hp_scale))

        total_waves = len(f_data["waves"])
        w_title = "БОСС!" if wave_idx == total_waves - 1 and ("БОСС" in b_id or self.current_floor_idx >= 2) else f"ВОЛНА {wave_idx + 1}/{total_waves}"
        self.fx.add_floating_text(f"{f_data['name']} — {w_title}", self.player.x, self.player.y - 80, TEXT_GOLD, size=28)
        self.sfx.play("dash")

    def enter_dojo(self):
        """Switches to the Training Dojo."""
        self.state = 'DOJO'
        self.player.x = MAP_WIDTH // 2
        self.player.y = MAP_HEIGHT // 2 + 200
        self.enemies.clear()
        self.active_abilities.clear()
        self.portal_active = False

        # Spawn immortal training dummies with different roles
        d1 = Enemy(MAP_WIDTH // 2 - 250, MAP_HEIGHT // 2 - 100, "stone_sentry", hp_scale=99.0)
        d1.name = "Манекен-Исполин (DPS Тест)"
        d1.max_hp = 99999
        d1.hp = 99999
        self.enemies.append(d1)

        d2 = Enemy(MAP_WIDTH // 2, MAP_HEIGHT // 2 - 100, "frost_shardling", hp_scale=99.0)
        d2.name = "Манекен Заморозки (Shatter Тест)"
        d2.max_hp = 99999
        d2.hp = 99999
        self.enemies.append(d2)

        d3 = Enemy(MAP_WIDTH // 2 + 250, MAP_HEIGHT // 2 - 100, "blood_inquisitor", hp_scale=99.0)
        d3.name = "Манекен Рокировки (Backstab Тест)"
        d3.max_hp = 99999
        d3.hp = 99999
        self.enemies.append(d3)

        self.fx.add_floating_text("ДОБРО ПОЖАЛОВАТЬ В ДОДЗЁ! БЕЗОПАСНАЯ ТРЕНИРОВКА КОМБО", self.player.x, self.player.y - 70, TEXT_CYAN, size=26)

    def leave_dojo(self):
        self.state = 'PLAYING'
        self.load_floor(self.current_floor_idx)

    def start_run(self):
        diff = DIFFICULTY_MANAGER.current
        CHALLENGE_MANAGER.reset_run_stats()
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
        self.player.game = self
        CHALLENGE_MANAGER.modify_player_on_start(self.player)
        self.score = 0
        only_curses = CHALLENGE_MANAGER.should_offer_only_curses()
        self.current_portal_offerings = generate_portal_offerings(1, curse_chance=(1.0 if only_curses else diff.curse_chance), only_curses=only_curses)
        self.state = 'PLAYING'
        self.load_floor(0)
        self.sfx.play("dash")
        ch_text = CHALLENGE_MANAGER.get_badge_text()
        start_msg = f"ЗАБЕГ НАЧАТ! {diff.name.upper()} {ch_text}".strip()
        self.fx.add_floating_text(start_msg, self.player.x, self.player.y - 70, (255, 90, 220) if ch_text else diff.color, size=28)

    def reset_run(self):
        self.start_run()

    def jump_to_floor_50(self):
        """Debug / Fast-travel helper: Loads Floor 50 and triggers Truth Boss encounter."""
        self.state = 'PLAYING'
        self.load_floor(49)
        self.fx.add_floating_text("ВХОД В ЧЕРТОГ ИСТИНЫ: 50 ЭТАЖ!", self.player.x, self.player.y - 90, TEXT_GOLD, size=28)

    def open_boss_dialogue(self):
        """Initiates the Floor 50 cinematic dialogue encounter with the Judge of Truth."""
        self.state = 'BOSS_DIALOGUE'
        self.dialogue_stage = 'QUESTION'
        self.dialogue_anim_time = 0.0
        self.dialogue_rects = {}
        self.dialogue_choice = None
        self.dialogue_boss_name = "ВЕРХОВНЫЙ СУДИЯ ИСТИНЫ [БОСС 50 ЭТАЖА]"
        self.dialogue_boss_title = "Хранитель 50-го Эшелона • Владыка Весов Судеб"
        self.dialogue_question_lines = [
            "Смертный... Ты преодолел 50 кругов преисподней и дерзнул ступить в Чертог Истины.",
            "Я зрю сквозь плоть и время, взвешивая твою душу на священных Весах Судьбы.",
            "Ответь мне перед ликом Вечности: ты прошёл игру без урона?"
        ]
        self.dialogue_result_title = ""
        self.dialogue_result_lines = []
        self.dialogue_result_color = TEXT_GOLD
        self.dialogue_damage_reported = 0

    def handle_boss_dialogue_choice(self, choice_idx):
        """Processes the player's answer (1: 'Да' / 2: 'Нет') and detects lies."""
        if self.dialogue_stage != 'QUESTION':
            return

        self.dialogue_choice = choice_idx
        damage_taken = getattr(self.player, 'total_damage_taken_run', 0.0)
        hits_taken = getattr(self.player, 'total_hits_taken_run', 0)
        self.dialogue_damage_reported = int(damage_taken)

        if choice_idx == 1:
            # Player said "Да, без урона!"
            if damage_taken > 0 or hits_taken > 0:
                # PLAYER LIED!
                self.dialogue_stage = 'ANSWER_LIED'
                self.dialogue_result_title = "ВРУНИШКА! ЖАЛКИЙ ЛЖЕЦ!"
                self.dialogue_result_color = (255, 60, 60)
                self.dialogue_result_lines = [
                    "Я чую запах твоей запекшейся крови и считаю каждый полученный шрам!",
                    f"Ты получил {int(damage_taken)} урона ({hits_taken} попаданий) за этот забег, но посмел солгать Судье!",
                    "Весы Правосудия обрушатся на тебя со всесокрушающей яростью за твой обман!"
                ]
                self.fx.add_screen_shake(30.0)
                self.sfx.play("crit")

                # Enrage the boss on floor 50!
                for en in self.enemies:
                    if en.id == "judge_of_truth":
                        en.enraged = True
                        en.speed *= 1.25
                        en.damage *= 1.20
                        self.fx.spawn_sparks(en.x, en.y, (255, 40, 60), count=55, speed=290)
                        self.fx.add_floating_text("В БЕШЕНСТВЕ ОТ ЛЖИ! (+25% СКОРОСТЬ)", en.x, en.y - 70, (255, 50, 50), size=26)

                # UNLOCK ACHIEVEMENT «Врунишка»
                ACHIEVEMENT_MANAGER.unlock("liar_achievement", self.fx, self.sfx)
            else:
                # TRUE NO-HIT GOD!
                self.dialogue_stage = 'ANSWER_NO_HIT'
                self.dialogue_result_title = "НЕВЕРОЯТНО... БОГ БЕЗУПРЕЧНОСТИ!"
                self.dialogue_result_color = (120, 240, 255)
                self.dialogue_result_lines = [
                    "Священные Весы неподвижны... Твои доспехи девственно чисты!",
                    "Ни единой царапины, ни капли крови за все 50 этажей преисподней!",
                    "Ты воистину величайший мастер клинка. Священный бой равных начинается!"
                ]
                self.fx.add_screen_shake(16.0)
                self.sfx.play("parry")
        elif choice_idx == 2:
            # Player said "Нет, я получал урон" (Truth)
            self.dialogue_stage = 'ANSWER_TRUTH'
            self.dialogue_result_title = "ЧЕСТНОСТЬ ПЕРЕД ЛИКОМ СУДЬБЫ"
            self.dialogue_result_color = (255, 215, 80)
            self.dialogue_result_lines = [
                "Твоя искренность достойна истинного воина клинка.",
                f"Шрамы (ты выдержал {int(damage_taken)} урона) лишь закаляют дух смертного.",
                "Ты не пытался обмануть Весы Истины. Докажи теперь силу своего духа в бою!"
            ]
            self.fx.add_screen_shake(12.0)
            self.sfx.play("parry")

    def close_boss_dialogue(self):
        """Ends the dialogue and starts the boss combat."""
        self.state = 'PLAYING'
        self.sfx.play("dash")
        self.fx.add_screen_shake(20.0)
        self.fx.add_floating_text("⚡ БИТВА ЗА СУДЬБУ: 50 ЭТАЖ! ⚡", self.player.x, self.player.y - 120, TEXT_GOLD, size=32)

    def draw_boss_dialogue(self, surface, anim_time, fonts):
        """Renders the cinematic Level 50 Boss Dialogue window and choices."""
        w, h = VIEW_WIDTH, VIEW_HEIGHT

        # 1. Dark atmospheric overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((6, 8, 14, 235))
        surface.blit(overlay, (0, 0))

        # 2. Main Dialogue Frame
        box_w, box_h = 960, 480
        bx = w // 2 - box_w // 2
        by = 110
        dlg_rect = pygame.Rect(bx, by, box_w, box_h)

        # Pulse border
        pulse = 0.5 + 0.5 * math.sin(anim_time * 5.0)
        border_glow = (
            int(255 * (0.8 + 0.2 * pulse)),
            int(215 * (0.8 + 0.2 * pulse)),
            int(60 * (0.8 + 0.2 * pulse))
        )
        bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg_surf.fill((12, 16, 26, 245))
        surface.blit(bg_surf, (bx, by))
        pygame.draw.rect(surface, border_glow, dlg_rect, 2, border_radius=8)

        # Inner decorative gold line
        inner_rect = pygame.Rect(bx + 6, by + 6, box_w - 12, box_h - 12)
        pygame.draw.rect(surface, (60, 50, 25), inner_rect, 1, border_radius=6)

        # 3. Boss Portrait / Crest (Left side)
        p_rect = pygame.Rect(bx + 24, by + 24, 150, 190)
        pygame.draw.rect(surface, (18, 22, 34), p_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 80), p_rect, 1, border_radius=6)

        # Draw Inquisitor boss sprite in portrait!
        inq_img = getattr(self.art, 'inquisitor_sprite', None)
        if inq_img:
            port_sprite = pygame.transform.smoothscale(inq_img, (120, 120))
            tint_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            tint_surf.fill((255, 215, 60, 60))
            port_sprite.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(port_sprite, (p_rect.centerx - 60, p_rect.y + 16))
        else:
            sym_f = fonts.get("sym_large", fonts["large"])
            s_icon = sym_f.render("⚖", True, (255, 220, 80))
            surface.blit(s_icon, (p_rect.centerx - s_icon.get_width() // 2, p_rect.y + 35))

        p_lbl = fonts["med"].render("СУДИЯ", True, TEXT_GOLD)
        surface.blit(p_lbl, (p_rect.centerx - p_lbl.get_width() // 2, p_rect.bottom - 44))
        p_sub = fonts["small"].render("50 ЭТАЖ", True, (200, 220, 240))
        surface.blit(p_sub, (p_rect.centerx - p_sub.get_width() // 2, p_rect.bottom - 24))

        # 4. Boss Title & Header
        title_x = bx + 195
        title_y = by + 24
        b_name = fonts["title"].render("ВЕРХОВНЫЙ СУДИЯ ИСТИНЫ", True, TEXT_GOLD)
        surface.blit(b_name, (title_x, title_y))

        b_tit = fonts["small"].render("[БОСС 50 ЭТАЖА] • Хранитель 50-го Эшелона • Владыка Весов Судеб", True, (190, 215, 245))
        surface.blit(b_tit, (title_x, title_y + 36))

        # Golden separator rule
        pygame.draw.line(surface, (90, 80, 50), (title_x, title_y + 60), (bx + box_w - 24, title_y + 60), 1)

        m_pos = pygame.mouse.get_pos()
        self.dialogue_rects = {}

        # 5. Content based on stage
        if self.dialogue_stage == 'QUESTION':
            # Speech lines
            sy = title_y + 72
            for line in self.dialogue_question_lines[:-1]:
                s_surf = fonts["med"].render(line, True, (220, 230, 245))
                surface.blit(s_surf, (title_x, sy))
                sy += 24

            # Main Question (Glowing highlight)
            q_surf = fonts["large"].render(f"«{self.dialogue_question_lines[-1].split(':')[-1].strip('«» ')}»", True, (255, 230, 100))
            surface.blit(q_surf, (title_x, sy + 6))

            # Option 1: "Да, ни единой царапины!" (Lie if took damage)
            opt1_rect = pygame.Rect(title_x, by + 235, 740, 78)
            self.dialogue_rects["opt1"] = opt1_rect
            is_hov1 = opt1_rect.collidepoint(m_pos)

            bg1 = (25, 34, 52) if is_hov1 else (16, 22, 34)
            bdr1 = (255, 215, 80) if is_hov1 else (70, 90, 130)
            pygame.draw.rect(surface, bg1, opt1_rect, border_radius=6)
            pygame.draw.rect(surface, bdr1, opt1_rect, 2 if is_hov1 else 1, border_radius=6)

            badge1 = pygame.Rect(opt1_rect.x + 12, opt1_rect.y + 14, 46, 50)
            pygame.draw.rect(surface, (20, 26, 42), badge1, border_radius=4)
            pygame.draw.rect(surface, (255, 215, 80), badge1, 1, border_radius=4)
            k1_s = fonts["large"].render("[1]", True, TEXT_GOLD)
            surface.blit(k1_s, (badge1.centerx - k1_s.get_width() // 2, badge1.centery - k1_s.get_height() // 2))

            t1_s = fonts["med"].render("«Да, ни единой царапины! Я прошел без единицы урона!»", True, TEXT_WHITE if not is_hov1 else TEXT_GOLD)
            surface.blit(t1_s, (opt1_rect.x + 70, opt1_rect.y + 14))
            sub1_s = fonts["small"].render("Заявить о безупречности забега  (Соврать Судье, если ты получал урон)", True, (180, 200, 225))
            surface.blit(sub1_s, (opt1_rect.x + 70, opt1_rect.y + 42))

            # Option 2: "Нет, меня ранили" (Truth)
            opt2_rect = pygame.Rect(title_x, by + 325, 740, 78)
            self.dialogue_rects["opt2"] = opt2_rect
            is_hov2 = opt2_rect.collidepoint(m_pos)

            bg2 = (22, 36, 46) if is_hov2 else (16, 22, 34)
            bdr2 = (120, 240, 255) if is_hov2 else (70, 90, 130)
            pygame.draw.rect(surface, bg2, opt2_rect, border_radius=6)
            pygame.draw.rect(surface, bdr2, opt2_rect, 2 if is_hov2 else 1, border_radius=6)

            badge2 = pygame.Rect(opt2_rect.x + 12, opt2_rect.y + 14, 46, 50)
            pygame.draw.rect(surface, (20, 26, 42), badge2, border_radius=4)
            pygame.draw.rect(surface, (120, 240, 255), badge2, 1, border_radius=4)
            k2_s = fonts["large"].render("[2]", True, TEXT_CYAN)
            surface.blit(k2_s, (badge2.centerx - k2_s.get_width() // 2, badge2.centery - k2_s.get_height() // 2))

            t2_s = fonts["med"].render("«Нет, меня ранили на этом тернистом пути.»", True, TEXT_WHITE if not is_hov2 else TEXT_CYAN)
            surface.blit(t2_s, (opt2_rect.x + 70, opt2_rect.y + 14))
            sub2_s = fonts["small"].render("Признать полученные раны  (Сказать чистую правду перед Весами Истины)", True, (180, 200, 225))
            surface.blit(sub2_s, (opt2_rect.x + 70, opt2_rect.y + 42))

            # Bottom hint
            hint_s = fonts["small"].render("Нажми клавишу [1] или [2] на клавиатуре, либо кликни ЛКМ по варианту ответа", True, (150, 170, 200))
            surface.blit(hint_s, (bx + box_w // 2 - hint_s.get_width() // 2, by + box_h - 32))

        else:
            # Result Stage (ANSWER_LIED / ANSWER_NO_HIT / ANSWER_TRUTH)
            res_y = title_y + 72
            hdr_surf = fonts["large"].render(self.dialogue_result_title, True, self.dialogue_result_color)
            surface.blit(hdr_surf, (title_x, res_y))
            res_y += 36

            if self.dialogue_stage == 'ANSWER_LIED':
                sym_m = fonts.get("sym_med", fonts["med"])
                star_s = sym_m.render("★", True, (255, 110, 195))
                ach_txt = fonts["med"].render(" РАЗБЛОКИРОВАНО СЕКРЕТНОЕ ДОСТИЖЕНИЕ: «ВРУНИШКА»! ", True, (255, 110, 195))
                surface.blit(star_s, (title_x, res_y))
                surface.blit(ach_txt, (title_x + star_s.get_width(), res_y))
                surface.blit(star_s, (title_x + star_s.get_width() + ach_txt.get_width(), res_y))
                res_y += 28

                sym_s = fonts.get("sym_small", fonts["small"])
                skull_s = sym_s.render("☠", True, (255, 90, 90))
                buff_txt = fonts["small"].render(" СУДИЯ РАЗЪЯРЕН ЛОЖЬЮ: СКОРОСТЬ +25%, УРОН +20%! ВЕСЫ СКЛОНИЛИСЬ ПРОТИВ ТЕБЯ!", True, (255, 90, 90))
                surface.blit(skull_s, (title_x, res_y))
                surface.blit(buff_txt, (title_x + skull_s.get_width() + 4, res_y))
                res_y += 28

            for line in self.dialogue_result_lines:
                s_surf = fonts["med"].render(line, True, (220, 235, 250))
                surface.blit(s_surf, (title_x, res_y))
                res_y += 25

            # Continue Button
            btn_w, btn_h = 440, 54
            btn_rect = pygame.Rect(bx + box_w // 2 - btn_w // 2, by + box_h - 76, btn_w, btn_h)
            self.dialogue_rects["btn_continue"] = btn_rect
            is_hov = btn_rect.collidepoint(m_pos)

            if self.dialogue_stage == 'ANSWER_LIED':
                b_bg = (55, 16, 24) if is_hov else (38, 12, 18)
                b_bdr = (255, 80, 80) if is_hov else (200, 50, 50)
                btn_txt = "[ ПРИНЯТЬ КАРУ! В БОЙ (ПРОБЕЛ) ]"
                txt_col = (255, 230, 230)
            elif self.dialogue_stage == 'ANSWER_NO_HIT':
                b_bg = (18, 45, 55) if is_hov else (12, 32, 40)
                b_bdr = (120, 240, 255) if is_hov else (70, 180, 210)
                btn_txt = "[ В СВЯЩЕННЫЙ БОЙ (ПРОБЕЛ) ]"
                txt_col = (220, 255, 255)
            else:
                b_bg = (45, 38, 18) if is_hov else (32, 26, 12)
                b_bdr = (255, 215, 80) if is_hov else (190, 160, 50)
                btn_txt = "[ НАЧАТЬ ПОЕДИНОК (ПРОБЕЛ) ]"
                txt_col = TEXT_GOLD

            pygame.draw.rect(surface, b_bg, btn_rect, border_radius=6)
            pygame.draw.rect(surface, b_bdr, btn_rect, 2, border_radius=6)
            b_s = fonts["large"].render(btn_txt, True, txt_col)
            surface.blit(b_s, (btn_rect.centerx - b_s.get_width() // 2, btn_rect.centery - b_s.get_height() // 2))

    def apply_perk(self, choice):
        if hasattr(self, 'current_portal_offerings') and self.current_portal_offerings:
            if 1 <= choice <= len(self.current_portal_offerings):
                offering = self.current_portal_offerings[choice - 1]
                offering.apply(self.player, self)
                if offering.is_cursed:
                    ACHIEVEMENT_MANAGER.unlock("curse_pact", self.fx, self.sfx)
        else:
            if choice == 1:
                self.player.max_hp += 40
                self.player.hp = self.player.max_hp
                self.fx.add_floating_text("+40 MAX HP & ПОЛНОЕ ИСЦЕЛЕНИЕ!", self.player.x, self.player.y - 70, (60, 240, 120), size=26)
            elif choice == 2:
                self.player.bonus_time_per_floor += 25.0
                self.fx.add_floating_text("+25s К ТАЙМЕРУ ЗОНЫ!", self.player.x, self.player.y - 70, TEXT_GOLD, size=26)
            elif choice == 3:
                self.player.bonus_damage_mult += 0.35
                self.fx.add_floating_text("+35% К УРОНУ ЗАКЛИНАНИЙ!", self.player.x, self.player.y - 70, (255, 80, 80), size=26)
        
        self.state = 'PLAYING'
        self.load_floor(self.current_floor_idx + 1)

    def cast_gesture_ability(self, raw_points):
        skill_id, score, tier, deviation = evaluate_gesture(raw_points)
        if not skill_id or tier == "INVALID":
            return

        CHALLENGE_MANAGER.on_glyph_drawn(self)
        ACHIEVEMENT_MANAGER.unlock("first_glyph", self.fx, self.sfx)

        skill = SKILL_INFO.get(skill_id)
        if not skill:
            return

        weapon = self.player.weapon
        accuracy_pct = int(score * 100)

        self.last_accuracy_info = {
            "name": skill["name"],
            "symbol": skill["symbol"],
            "score": accuracy_pct,
            "tier": tier,
            "color": skill["color"]
        }

        # Cursor in world coordinates
        screen_mx, screen_my = pygame.mouse.get_pos()
        world_mx = screen_mx + self.cam_x
        world_my = screen_my + self.cam_y

        base_angle = math.atan2(world_my - self.player.y, world_mx - self.player.x)
        eff_angle = base_angle + math.radians(deviation)

        # Fumble penalty
        if tier == "FUMBLE":
            self.player.fumble_timer = weapon.fumble_stun
            self.player.combo_count = 0
            self.last_gesture_id = None
            self.fx.add_screen_shake(8.0)
            self.fx.spawn_sparks(self.player.x, self.player.y, (255, 40, 40), count=16)
            self.fx.add_floating_text(f"ОСЕЧКА! ({accuracy_pct}%) - СРЫВ ЗНАКА", self.player.x, self.player.y - 45, (255, 60, 60), size=24)
            self.sfx.play("fumble")
            return

        self.player.combo_count += 1
        self.player.combo_timer = weapon.combo_window
        combo_mult = 1.0 + (self.player.combo_count - 1) * 0.30

        if tier == "PERFECT":
            acc_dmg_mult = 1.6
            badge_text = f"★ PERFECT {accuracy_pct}%! CRIT!"
            badge_color = TEXT_GOLD
            self.fx.add_screen_shake(12.0)
            self.sfx.play("crit")
        elif tier == "CLEAN":
            acc_dmg_mult = 1.0
            badge_text = f"CLEAN {accuracy_pct}%"
            badge_color = TEXT_CYAN
            self.fx.add_screen_shake(5.0)
            self.sfx.play("slash")
        else: # SLOPPY
            acc_dmg_mult = 0.45
            badge_text = f"SLOPPY {accuracy_pct}% (Увод)"
            badge_color = (255, 170, 50)
            self.fx.add_screen_shake(3.0)
            self.sfx.play("slash")

        total_damage_mult = weapon.damage_mult * acc_dmg_mult * combo_mult * self.player.bonus_damage_mult
        if self.player.combo_count >= 3:
            total_damage_mult *= 2.0
            self.fx.add_floating_text("★★★ ФИНИШЕР СЕРИИ x3! ДВОЙНОЙ УРОН! ★★★", self.player.x, self.player.y - 75, TEXT_GOLD, size=28)
            self.fx.add_screen_shake(18.0)
            self.sfx.play("crit")
            self.player.combo_count = 0

        self.fx.add_floating_text(badge_text, self.player.x, self.player.y - 50, badge_color, size=22)
        self.player.recovery_timer = 0.18 * weapon.recovery_mult

        now = self.anim_time
        time_since_last = now - self.last_gesture_time

        # =====================================================================
        # COMPOUND MULTI-RUNE SYNTHESIS CHECK!
        # =====================================================================
        is_fusion = False
        fusion_mult = total_damage_mult * (1.0 + getattr(self.player, 'fusion_damage_bonus', 0.0))

        # 1. [|] Метеорит + [V] Лед => КРИО-МЕТЕОРИТ (Glacial Comet)
        if time_since_last < 1.6 and (
            (self.last_gesture_id == "SLASH_V" and skill_id == "PARRY") or
            (self.last_gesture_id == "PARRY" and skill_id == "SLASH_V")
        ):
            self.active_abilities.append(GlacialCometFusion(world_mx, world_my, fusion_mult * 1.4))
            self.fx.add_floating_text("★ СИНТЕЗ: КРИО-МЕТЕОРИТ [| + V]! ЗАМОРОЗКА ПО ОБЛАСТИ!", world_mx, world_my - 60, (140, 230, 255), size=28)
            self.sfx.play("crit")
            is_fusion = True

        # 2. [O] Черная Дыра + [^] Огонь => ОГНЕННАЯ СИНГУЛЯРНОСТЬ
        elif time_since_last < 1.6 and (
            (self.last_gesture_id == "CIRCLE" and skill_id == "UPPERCUT") or
            (self.last_gesture_id == "UPPERCUT" and skill_id == "CIRCLE")
        ):
            self.active_abilities.append(FirestormVortexFusion(world_mx, world_my, fusion_mult * 1.35))
            self.fx.add_floating_text("★ СИНТЕЗ: ИНФЕРНАЛЬНАЯ ВОРОНКА [O + ^]!", world_mx, world_my - 60, (255, 140, 30), size=28)
            self.sfx.play("crit")
            is_fusion = True

        # 3. [|] Метеорит + [Z] Молния => ГРОМОВОЙ РАСКОЛ
        elif time_since_last < 1.6 and (
            (self.last_gesture_id == "SLASH_V" and skill_id == "ZIGZAG") or
            (self.last_gesture_id == "ZIGZAG" and skill_id == "SLASH_V")
        ):
            self.active_abilities.append(ThunderMeteorFusion(world_mx, world_my, fusion_mult * 1.45))
            self.fx.add_floating_text("★ СИНТЕЗ: ГРОМОВОЙ РАСКОЛ [| + Z]!", world_mx, world_my - 60, (255, 255, 100), size=28)
            self.sfx.play("crit")
            is_fusion = True

        # 4. [O] Черная Дыра + [>] Жатва => КРОВАВЫЙ ВИХРЬ
        elif time_since_last < 1.6 and (
            (self.last_gesture_id == "CIRCLE" and skill_id == "THRUST") or
            (self.last_gesture_id == "THRUST" and skill_id == "CIRCLE")
        ):
            self.active_abilities.append(BloodVortexFusion(world_mx, world_my, fusion_mult * 1.3))
            self.fx.add_floating_text("★ СИНТЕЗ: КРОВАВЫЙ ВИХРЬ [O + >]! ОТХИЛ +45 HP!", world_mx, world_my - 60, (255, 40, 70), size=28)
            self.sfx.play("crit")
            is_fusion = True

        # 5. [X] Крест + [—] Срез => ПРОСТРАНСТВЕННЫЙ РАЗРЫВ
        elif time_since_last < 1.6 and (
            (self.last_gesture_id == "CROSS" and skill_id == "SLASH_H") or
            (self.last_gesture_id == "SLASH_H" and skill_id == "CROSS")
        ):
            self.active_abilities.append(DimensionalRiftFusion(world_mx, world_my, fusion_mult * 1.55))
            self.fx.add_floating_text("★ СИНТЕЗ: ПРОСТРАНСТВЕННЫЙ РАЗРЫВ [X + —]!", world_mx, world_my - 60, (140, 240, 255), size=28)
            self.sfx.play("crit")
            is_fusion = True

        # 6. [△] Призма + [★] Звезда => СВЕТОВОЙ КАТАКЛИЗМ
        elif time_since_last < 1.6 and (
            (self.last_gesture_id == "TRIANGLE" and skill_id == "STAR_PENTAGRAM") or
            (self.last_gesture_id == "STAR_PENTAGRAM" and skill_id == "TRIANGLE")
        ):
            self.active_abilities.append(HolyPrismaticNovaFusion(world_mx, world_my, fusion_mult * 1.65))
            self.fx.add_floating_text("★ СИНТЕЗ: СВЕТОВОЙ КАТАКЛИЗМ [△ + ★]!", world_mx, world_my - 60, (255, 255, 180), size=28)
            self.sfx.play("crit")
            is_fusion = True

        # 7. [🛡] Щит + [⌛] Часы => АБСОЛЮТНЫЙ ХРОНО-СТАЗИС
        elif time_since_last < 1.6 and (
            (self.last_gesture_id == "SHIELD_BLOCK" and skill_id == "HOURGLASS_SWAP") or
            (self.last_gesture_id == "HOURGLASS_SWAP" and skill_id == "SHIELD_BLOCK")
        ):
            self.bullet_time_timer = 4.5
            self.player.i_frame_timer = 4.5
            for en in self.enemies:
                if en.alive:
                    en.stun_timer = max(en.stun_timer, 4.0)
            self.fx.add_floating_text("★ СИНТЕЗ: ХРОНО-СТАЗИС [🛡 + ⌛]! ПОЛНЫЙ СТОП ВРЕМЕНИ 4с!", world_mx, world_my - 60, (210, 100, 255), size=28)
            self.fx.add_screen_shake(16.0)
            self.sfx.play("parry")
            is_fusion = True

        # Store for next fusion
        self.last_gesture_id = skill_id
        self.last_gesture_time = now

        if is_fusion:
            ACHIEVEMENT_MANAGER.unlock("first_fusion", self.fx, self.sfx)
            self.combo_gesture_chain.clear()
            return # Fusion successfully consumed the compound cast!

        # Multi-glyph sequence chain buffer (min 3, up to 5 signs for Ultra-Combos!)
        self.combo_gesture_chain.append((skill_id, now))
        self.combo_gesture_chain = [(g, t) for g, t in self.combo_gesture_chain if now - t <= 3.2]
        if len(self.combo_gesture_chain) > 5:
            self.combo_gesture_chain.pop(0)

        # Check for 3, 4, or 5 sign Ultra-Combo synthesis!
        if len(self.combo_gesture_chain) >= 3:
            chain_keys = [g for g, _ in self.combo_gesture_chain]
            resolved = COMBO_MATRIX.resolve_combo(chain_keys)
            if resolved:
                ultra_spell = resolved["creator"](world_mx, world_my, total_damage_mult * resolved["mult"])
                self.active_abilities.append(ultra_spell)
                self.fx.add_floating_text(f"★★★ {resolved['name']}! ★★★", world_mx, world_my - 75, resolved["color"], size=30)
                self.fx.add_screen_shake(26.0)
                self.sfx.play("crit")
                ACHIEVEMENT_MANAGER.unlock("ultra_combo_cast", self.fx, self.sfx)
                self.combo_gesture_chain.clear()
                return

        # =====================================================================
        # STANDARD HIGH-IMPACT ABILITIES
        # =====================================================================
        atype = skill["type"]

        if atype == "shield_block":
            self.bullet_time_timer = 3.2
            self.player.i_frame_timer = 3.2
            self.fx.add_screen_shake(10.0)
            self.fx.spawn_sparks(self.player.x, self.player.y, (255, 230, 80), count=35, speed=280)
            self.fx.add_floating_text("★ БАСТИОН: ВРЕМЯ ЗАМЕДЛЕНО В 5 РАЗ!", self.player.x, self.player.y - 45, TEXT_GOLD, size=26)
            self.sfx.play("parry")
            ACHIEVEMENT_MANAGER.unlock("slo_mo_parry", self.fx, self.sfx)

        elif atype == "swap_position":
            target = None
            min_dist = float('inf')
            for en in self.enemies:
                if en.alive:
                    d = math.hypot(world_mx - en.x, world_my - en.y)
                    if d < min_dist:
                        min_dist = d
                        target = en

            if target:
                px, py = self.player.x, self.player.y
                ex, ey = target.x, target.y
                self.player.x, self.player.y = ex, ey
                target.x, target.y = px, py
                target.stun_timer = 1.4
                target.is_attacking = False
                target.backstab_vulnerable = True
                
                self.fx.spawn_sparks(px, py, (210, 100, 255), count=25, speed=220)
                self.fx.spawn_sparks(ex, ey, (210, 100, 255), count=25, speed=220)
                self.fx.add_screen_shake(12.0)
                self.fx.add_floating_text("★ РОКИРОВКА! BACKSTAB +200%", self.player.x, self.player.y - 40, TEXT_PURPLE, size=26)
                self.sfx.play("dash")
            else:
                self.fx.add_floating_text("НЕТ ВРАГА ДЛЯ РОКИРОВКИ", world_mx, world_my - 20, (180, 160, 200), size=18)

        elif atype == "cataclysm_star":
            self.active_abilities.append(PentagramCataclysm(world_mx, world_my, total_damage_mult))
            self.zone_timer += 15.0
            self.fx.add_floating_text("★ АПОКАЛИПСИС: +15s TIME!", world_mx, world_my - 50, TEXT_GOLD, size=28)
            self.sfx.play("crit")

        elif atype == "vortex":
            self.active_abilities.append(BlackHoleVortex(world_mx, world_my, total_damage_mult))
            self.sfx.play("dash")
            self.fx.add_floating_text("СИНГУЛЯРНОСТЬ!", world_mx, world_my - 30, (180, 80, 255), size=26)

        elif atype == "fire_fissure":
            self.active_abilities.append(FireFissure(self.player.x, self.player.y, eff_angle, total_damage_mult))
            self.sfx.play("slash")
            self.fx.add_screen_shake(8.0)
            self.fx.add_floating_text("ИНФЕРНО!", self.player.x, self.player.y - 30, (255, 120, 30), size=24)

        elif atype == "frost_stasis":
            target = None
            min_dist = 280.0
            for en in self.enemies:
                if en.alive:
                    d = math.hypot(world_mx - en.x, world_my - en.y)
                    if d < min_dist:
                        min_dist = d
                        target = en
            if target:
                self.active_abilities.append(GlacialStasis(target, total_damage_mult, self.player))
                self.sfx.play("parry")
                self.fx.spawn_sparks(target.x, target.y, (160, 230, 255), count=25, speed=220)
                self.fx.add_floating_text("ЗАМОРОЗКА! (x2.5 SHATTER)", target.x, target.y - 45, (140, 230, 255), size=26)

        elif atype == "meteor":
            self.active_abilities.append(MeteorImpact(world_mx, world_my, total_damage_mult))
            self.sfx.play("dash")
            self.fx.add_floating_text("МЕТЕОРИТ!", world_mx, world_my - 30, (255, 90, 30), size=26)

        elif atype == "lightning":
            cast_chain_lightning(self.player, self.enemies, total_damage_mult, self.fx, self.sfx)
            self.player.i_frame_timer = 0.25

        elif atype == "dimensional_slash":
            dash_len = 210.0
            self.fx.add_slash(self.player.x, self.player.y, eff_angle, "SLASH_H", (120, 240, 255))
            self.player.vx = math.cos(eff_angle) * 880.0
            self.player.vy = math.sin(eff_angle) * 880.0
            self.player.i_frame_timer = 0.32
            self.sfx.play("dash")

            for en in self.enemies:
                if en.alive and math.hypot(en.x - self.player.x, en.y - self.player.y) < 160:
                    dmg = 48.0 * total_damage_mult
                    en.take_hit(dmg, math.cos(eff_angle) * 280, math.sin(eff_angle) * 280, 0.4, False, self.fx, self.sfx, spell_tag="БАЗОВЫЙ РАЗРЕЗ", player=self.player)
                    self.fx.add_floating_text(f"-{int(dmg)}", en.x, en.y - 25, (120, 240, 255), size=24)

        elif atype == "cross_slash":
            self.active_abilities.append(CrossSlashAbility(world_mx, world_my, total_damage_mult))
            self.sfx.play("slash")

        elif atype == "prismatic_barrier":
            self.active_abilities.append(PrismaticBarrierAbility(self.player.x, self.player.y, total_damage_mult))
            self.sfx.play("parry")
            self.fx.add_floating_text("ЭГИДА ПРИЗМЫ!", self.player.x, self.player.y - 35, (100, 255, 200), size=26)

        elif atype == "infinite_barrage":
            self.active_abilities.append(InfiniteBladeBarrageAbility(world_mx, world_my, total_damage_mult))
            self.sfx.play("slash")
            self.fx.add_floating_text("ПЕТЛЯ БЕСКОНЕЧНОСТИ (OMNISLASH)!", world_mx, world_my - 35, (220, 120, 255), size=26)

        elif atype == "custom_strike":
            self.active_abilities.append(CustomStrikeAbility(world_mx, world_my, total_damage_mult * 1.5))
            self.sfx.play("crit")
            self.fx.add_floating_text("✦ ЗНАК ВЛАДЫКИ: СВЕРХУДАР!", world_mx, world_my - 45, (255, 235, 90), size=30)


    def run(self):
        running = True
        while running:
            real_dt = min(self.clock.tick(FPS) / 1000.0, 0.1)

            # -------------------------------------------------------------
            # INPUT HANDLING
            # -------------------------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # MAIN MENU Navigation
                    if self.state == 'MAIN_MENU':
                        if event.key in (pygame.K_1, pygame.K_RETURN, pygame.K_SPACE):
                            self.start_run()
                        elif event.key == pygame.K_2:
                            self.state = 'DIFFICULTY_SELECT'
                            self.sfx.play("parry")
                        elif event.key == pygame.K_3:
                            self.state = 'ACHIEVEMENTS_MENU'
                            self.sfx.play("parry")
                        elif event.key == pygame.K_4:
                            self.enter_dojo()
                        elif event.key in (pygame.K_5, pygame.K_k):
                            self.state = 'CUSTOM_GLYPH_FORGE'
                            self.custom_points = []
                            self.custom_glyph_feedback = "Зажми ЛКМ/ПКМ и нарисуй свой символ в золотом квадрате!"
                            self.sfx.play("parry")
                        elif event.key in (pygame.K_6, pygame.K_ESCAPE, pygame.K_q):
                            running = False

                    # DIFFICULTY SELECTION & CHALLENGES Keys
                    elif self.state == 'DIFFICULTY_SELECT':
                        if event.key in (pygame.K_TAB, pygame.K_q, pygame.K_e):
                            self.diff_modal_tab = 1 - getattr(self, 'diff_modal_tab', 0)
                            self.sfx.play("parry")
                        elif getattr(self, 'diff_modal_tab', 0) == 0:
                            if event.key == pygame.K_1:
                                DIFFICULTY_MANAGER.set_difficulty("APPRENTICE")
                                self.sfx.play("parry")
                            elif event.key == pygame.K_2:
                                DIFFICULTY_MANAGER.set_difficulty("ADEPT")
                                self.sfx.play("parry")
                            elif event.key == pygame.K_3:
                                DIFFICULTY_MANAGER.set_difficulty("INQUISITOR")
                                self.sfx.play("parry")
                            elif event.key == pygame.K_4:
                                DIFFICULTY_MANAGER.set_difficulty("NIGHTMARE")
                                self.sfx.play("parry")
                            elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                                self.state = 'MAIN_MENU'
                                self.sfx.play("dash")
                        else:
                            # Challenges Tab Keys (1-7 toggle individual challenges, A all, C clear, P/H/G presets)
                            ch_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7]
                            if event.key in ch_keys:
                                ch_idx = ch_keys.index(event.key)
                                if ch_idx < len(CHALLENGE_ORDER):
                                    CHALLENGE_MANAGER.toggle(CHALLENGE_ORDER[ch_idx])
                                    self.sfx.play("parry")
                            elif event.key == pygame.K_a:
                                CHALLENGE_MANAGER.enable_all()
                                self.sfx.play("crit")
                            elif event.key == pygame.K_c:
                                CHALLENGE_MANAGER.disable_all()
                                self.sfx.play("dash")
                            elif event.key == pygame.K_p:
                                CHALLENGE_MANAGER.apply_preset_only_curses()
                                self.sfx.play("crit")
                            elif event.key == pygame.K_h:
                                CHALLENGE_MANAGER.apply_preset_titan_hell()
                                self.sfx.play("crit")
                            elif event.key == pygame.K_g:
                                CHALLENGE_MANAGER.apply_preset_glass_nightmare()
                                self.sfx.play("crit")
                            elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                                self.state = 'MAIN_MENU'
                                self.sfx.play("dash")

                    # ACHIEVEMENTS MENU Keys
                    elif self.state == 'ACHIEVEMENTS_MENU':
                        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                            self.state = 'MAIN_MENU'
                            self.sfx.play("dash")
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            self.achievements_page = max(0, self.achievements_page - 1)
                            self.sfx.play("dash")
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            tot_p = self.ach_menu_rects.get("total_pages", 1)
                            self.achievements_page = min(tot_p - 1, self.achievements_page + 1)
                            self.sfx.play("dash")

                    # Toggle Pause
                    elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                        if self.state in ('PLAYING', 'DOJO'):
                            self.state = 'PAUSED'
                        elif self.state == 'PAUSED':
                            self.state = 'PLAYING'
                        elif self.state == 'TOME_OF_SYNTHESIS':
                            self.state = 'PLAYING'
                        elif self.state in ('DIFFICULTY_SELECT', 'ACHIEVEMENTS_MENU'):
                            self.state = 'MAIN_MENU'

                    # Return to Main Menu from Pause or Death
                    elif event.key == pygame.K_m and (self.state == 'PAUSED' or not self.player.alive):
                        self.state = 'MAIN_MENU'
                        self.sfx.play("dash")

                    # Interact: Pick up weapon or open Grimoire Lectern: E
                    elif event.key == pygame.K_e and self.state in ('PLAYING', 'DOJO'):
                        # Check nearby dropped weapon first
                        closest_dw = None
                        min_dist = 70.0
                        for dw in self.dropped_weapons:
                            if dw.alive:
                                d = math.hypot(self.player.x - dw.x, self.player.y - dw.y)
                                if d < min_dist:
                                    min_dist = d
                                    closest_dw = dw

                        if closest_dw:
                            old_wep = self.player.weapon
                            # Equip new weapon into active slot
                            self.player.equip_weapon(closest_dw.weapon)
                            # Swap dropped weapon on ground with player's previous weapon
                            closest_dw.weapon = old_wep
                            closest_dw.x = self.player.x
                            closest_dw.y = self.player.y

                            # Audio & Visual FX
                            cur_w = self.player.weapon
                            self.fx.spawn_sparks(self.player.x, self.player.y, cur_w.glow_color, count=36, speed=230)
                            if cur_w.tier == 5:
                                self.fx.add_screen_shake(22.0)
                                self.sfx.play("crit")
                                self.fx.add_floating_text(f"ВЗЯТО: {cur_w.name}", self.player.x, self.player.y - 75, (255, 255, 255), size=28)
                                ACHIEVEMENT_MANAGER.unlock("divine_weapon_pickup", self.fx, self.sfx)
                            elif cur_w.tier >= 4:
                                self.fx.add_screen_shake(12.0)
                                self.sfx.play("crit")
                                self.fx.add_floating_text(f"ВЗЯТО: {cur_w.name}", self.player.x, self.player.y - 55, cur_w.glow_color, size=24)
                            else:
                                self.sfx.play("parry")
                                self.fx.add_floating_text(f"ВЗЯТО: {cur_w.name}", self.player.x, self.player.y - 50, cur_w.glow_color, size=22)

                            # Check Arsenal Master achievement
                            if all(w.tier >= 3 for w in self.player.weapon_slots.values()):
                                ACHIEVEMENT_MANAGER.unlock("arsenal_master", self.fx, self.sfx)
                        else:
                            # Grimoire Lectern interaction
                            d_lectern = math.hypot(self.player.x - self.lectern_pos[0], self.player.y - self.lectern_pos[1])
                            if d_lectern < 100:
                                self.state = 'TOME_OF_SYNTHESIS'
                                self.sfx.play("parry")

                    # Training Dojo toggle: T
                    elif event.key == pygame.K_t:
                        if self.state == 'DOJO':
                            self.leave_dojo()
                        else:
                            self.enter_dojo()

                    # Combo Forge Menu toggle: C
                    elif event.key == pygame.K_c:
                        if self.state == 'COMBO_FORGE_MENU':
                            self.state = 'PLAYING'
                        else:
                            self.state = 'COMBO_FORGE_MENU'
                            self.forge_points = []
                            self.forge_feedback = "Черти знаки связкой (минимум 3, максимум 5 знаков)!"

                    elif self.state == 'COMBO_FORGE_MENU':
                        if event.key == pygame.K_SPACE:
                            if len(self.forge_slots) >= 3:
                                resolved = COMBO_MATRIX.resolve_combo(self.forge_slots)
                                self.fx.add_screen_shake(20.0)
                                self.sfx.play("crit")
                                self.forge_feedback = f"ТЕСТ: {resolved['name']} сработал с уроном x{resolved['mult']:.2f}!"
                            else:
                                self.forge_feedback = "Сначала начерти минимум 3 знака для комбо!"
                        elif event.key == pygame.K_RETURN:
                            if len(self.forge_slots) >= 3:
                                resolved = COMBO_MATRIX.resolve_combo(self.forge_slots)
                                self.sealed_ultra_combo = resolved
                                self.sfx.play("crit")
                                self.forge_feedback = f"★ УЛЬТРА-КОМБО «{resolved['name']}» ЗАПЕЧАТАНО В СЛОТ!"
                            else:
                                self.forge_feedback = "Нужно минимум 3 знака для запечатывания комбо!"
                        elif event.key == pygame.K_BACKSPACE:
                            self.forge_slots.clear()
                            self.forge_feedback = "Слоты очищены. Начерти новую связку из 3-5 знаков!"
                        elif event.key in (pygame.K_ESCAPE, pygame.K_c):
                            self.state = 'PLAYING'

                    # Custom Glyph Studio toggle: K
                    elif event.key == pygame.K_k:
                        if self.state == 'CUSTOM_GLYPH_FORGE':
                            self.state = 'DOJO'
                        else:
                            self.state = 'CUSTOM_GLYPH_FORGE'
                            self.custom_points = []
                            self.custom_glyph_feedback = "Зажми ЛКМ/ПКМ и нарисуй свой символ в золотом квадрате!"

                    elif self.state == 'CUSTOM_GLYPH_FORGE':
                        if event.key == pygame.K_RETURN:
                            if len(self.custom_points) >= 4:
                                register_custom_glyph(self.custom_points, "CUSTOM_GLYPH")
                                self.custom_glyph_recorded = True
                                self.custom_glyph_feedback = "★ ЗНАК УСПЕШНО СОХРАНЕН! Теперь черти его в бою! [ESC / K]"
                                self.sfx.play("crit")
                                self.fx.add_screen_shake(12.0)
                                ACHIEVEMENT_MANAGER.unlock("custom_glyph_creator", self.fx, self.sfx)
                            else:
                                self.custom_glyph_feedback = "Слишком мало точек! Нарисуй четкий знак."
                        elif event.key == pygame.K_BACKSPACE:
                            self.custom_points = []
                            self.custom_glyph_feedback = "Холст очищен. Нарисуй новый знак!"
                        elif event.key == pygame.K_ESCAPE:
                            self.state = 'MAIN_MENU'

                    # Quick restart run
                    elif event.key == pygame.K_r:
                        self.reset_run()

                    # Floor 50 Boss & Damage Test Shortcuts
                    elif event.key == pygame.K_F5 and self.state in ('PLAYING', 'PAUSED', 'DOJO'):
                        self.jump_to_floor_50()
                    elif event.key == pygame.K_F6 and self.state in ('PLAYING', 'PAUSED', 'DOJO'):
                        self.player.take_damage(20.0, self.fx, self.sfx, self.art, False)
                        self.fx.add_floating_text("ТЕСТ: +20 УРОНА ПОЛУЧЕНО!", self.player.x, self.player.y - 70, (255, 60, 60), size=24)
                    elif event.key == pygame.K_F7 and self.state in ('PLAYING', 'PAUSED', 'DOJO'):
                        self.player.total_damage_taken_run = 0.0
                        self.player.total_hits_taken_run = 0
                        self.player.hp = self.player.max_hp
                        self.fx.add_floating_text("ТЕСТ: УРОН СБРОШЕН (0 HP NO-HIT)!", self.player.x, self.player.y - 70, (120, 240, 255), size=24)

                    # Boss Dialogue Keyboard Controls
                    elif self.state == 'BOSS_DIALOGUE':
                        if self.dialogue_stage == 'QUESTION':
                            if event.key == pygame.K_1:
                                self.handle_boss_dialogue_choice(1)
                            elif event.key == pygame.K_2:
                                self.handle_boss_dialogue_choice(2)
                        elif self.dialogue_stage in ('ANSWER_LIED', 'ANSWER_NO_HIT', 'ANSWER_TRUTH'):
                            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_1, pygame.K_2):
                                self.close_boss_dialogue()

                    # Quit in pause menu
                    elif event.key == pygame.K_q and self.state == 'PAUSED':
                        running = False

                    # Perk selection keys
                    elif self.state == 'PERK_SELECTION':
                        if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            choice = int(event.unicode)
                            self.apply_perk(choice)

                    # Weapon switch between carried slots during play
                    elif self.state in ('PLAYING', 'DOJO') and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        w_slot = int(event.unicode)
                        if hasattr(self.player, 'switch_weapon_slot') and self.player.switch_weapon_slot(w_slot):
                            w = self.player.weapon
                            self.sfx.play("dash")
                            self.fx.spawn_sparks(self.player.x, self.player.y, w.glow_color, count=16, speed=170)
                            self.fx.add_floating_text(f"[{w_slot}] {w.name} ({w.short_tier})", self.player.x, self.player.y - 50, w.glow_color, size=22)

                    # Cast Sealed Ultra-Combo: F
                    elif event.key == pygame.K_f and self.state in ('PLAYING', 'DOJO'):
                        if self.sealed_ultra_combo:
                            world_mx = self.cam_x + pygame.mouse.get_pos()[0]
                            world_my = self.cam_y + pygame.mouse.get_pos()[1]
                            ultra = self.sealed_ultra_combo["creator"](world_mx, world_my, self.player.weapon.damage_mult * self.sealed_ultra_combo["mult"])
                            self.active_abilities.append(ultra)
                            self.fx.add_floating_text(f"★★★ {self.sealed_ultra_combo['name']}! ★★★", world_mx, world_my - 75, self.sealed_ultra_combo["color"], size=30)
                            self.fx.add_screen_shake(28.0)
                            self.sfx.play("crit")
                            ACHIEVEMENT_MANAGER.unlock("ultra_combo_cast", self.fx, self.sfx)
                            self.sealed_ultra_combo = None
                        else:
                            self.fx.add_floating_text("НЕТ ЗАПЕЧАТАННОГО КОМБО! Нажми [C] для синтеза", self.player.x, self.player.y - 45, (255, 120, 120), size=20)

                # Main Menu Mouse Click
                elif self.state == 'MAIN_MENU':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                        m_pos = event.pos
                        if self.menu_buttons.get("START") and self.menu_buttons["START"].collidepoint(m_pos):
                            self.start_run()
                        elif self.menu_buttons.get("DIFFICULTY") and self.menu_buttons["DIFFICULTY"].collidepoint(m_pos):
                            self.state = 'DIFFICULTY_SELECT'
                            self.sfx.play("parry")
                        elif self.menu_buttons.get("ACHIEVEMENTS") and self.menu_buttons["ACHIEVEMENTS"].collidepoint(m_pos):
                            self.state = 'ACHIEVEMENTS_MENU'
                            self.sfx.play("parry")
                        elif self.menu_buttons.get("DOJO") and self.menu_buttons["DOJO"].collidepoint(m_pos):
                            self.enter_dojo()
                        elif self.menu_buttons.get("CUSTOM_GLYPH") and self.menu_buttons["CUSTOM_GLYPH"].collidepoint(m_pos):
                            self.state = 'CUSTOM_GLYPH_FORGE'
                            self.custom_points = []
                            self.custom_glyph_feedback = "Зажми ЛКМ/ПКМ и нарисуй свой символ в золотом квадрате!"
                            self.sfx.play("parry")
                        elif self.menu_buttons.get("QUIT") and self.menu_buttons["QUIT"].collidepoint(m_pos):
                            running = False

                # Difficulty Selection & Challenges Mouse Click
                elif self.state == 'DIFFICULTY_SELECT':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                        m_pos = event.pos
                        if self.diff_modal_rects.get("btn_back") and self.diff_modal_rects["btn_back"].collidepoint(m_pos):
                            self.state = 'MAIN_MENU'
                            self.sfx.play("dash")
                        elif self.diff_modal_rects.get("btn_tab_diff") and self.diff_modal_rects["btn_tab_diff"].collidepoint(m_pos):
                            self.diff_modal_tab = 0
                            self.sfx.play("parry")
                        elif self.diff_modal_rects.get("btn_tab_chal") and self.diff_modal_rects["btn_tab_chal"].collidepoint(m_pos):
                            self.diff_modal_tab = 1
                            self.sfx.play("parry")
                        elif self.diff_modal_rects.get("btn_chal_banner") and self.diff_modal_rects["btn_chal_banner"].collidepoint(m_pos):
                            self.diff_modal_tab = 1
                            self.sfx.play("parry")
                        elif getattr(self, 'diff_modal_tab', 0) == 0:
                            for d_key, r in self.diff_modal_rects.get("card_rects", {}).items():
                                if r.collidepoint(m_pos):
                                    DIFFICULTY_MANAGER.set_difficulty(d_key)
                                    self.sfx.play("parry")
                                    break
                        else:
                            # Challenges Tab clicks
                            clicked_ch = False
                            for ch_key, r in self.diff_modal_rects.get("challenge_rects", {}).items():
                                if r.collidepoint(m_pos):
                                    CHALLENGE_MANAGER.toggle(ch_key)
                                    self.sfx.play("parry")
                                    clicked_ch = True
                                    break
                            if not clicked_ch:
                                presets = self.diff_modal_rects.get("preset_rects", {})
                                if presets.get("all") and presets["all"].collidepoint(m_pos):
                                    CHALLENGE_MANAGER.enable_all()
                                    self.sfx.play("crit")
                                elif presets.get("clear") and presets["clear"].collidepoint(m_pos):
                                    CHALLENGE_MANAGER.disable_all()
                                    self.sfx.play("dash")
                                elif presets.get("only_curses") and presets["only_curses"].collidepoint(m_pos):
                                    CHALLENGE_MANAGER.apply_preset_only_curses()
                                    self.sfx.play("crit")
                                elif presets.get("titan_hell") and presets["titan_hell"].collidepoint(m_pos):
                                    CHALLENGE_MANAGER.apply_preset_titan_hell()
                                    self.sfx.play("crit")
                                elif presets.get("glass_nightmare") and presets["glass_nightmare"].collidepoint(m_pos):
                                    CHALLENGE_MANAGER.apply_preset_glass_nightmare()
                                    self.sfx.play("crit")

                # Achievements Menu Mouse Click
                elif self.state == 'ACHIEVEMENTS_MENU':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                        m_pos = event.pos
                        if self.ach_menu_rects.get("btn_back") and self.ach_menu_rects["btn_back"].collidepoint(m_pos):
                            self.state = 'MAIN_MENU'
                            self.sfx.play("dash")
                        elif self.ach_menu_rects.get("btn_prev") and self.ach_menu_rects["btn_prev"].collidepoint(m_pos):
                            self.achievements_page = max(0, self.achievements_page - 1)
                            self.sfx.play("dash")
                        elif self.ach_menu_rects.get("btn_next") and self.ach_menu_rects["btn_next"].collidepoint(m_pos):
                            tot_p = self.ach_menu_rects.get("total_pages", 1)
                            self.achievements_page = min(tot_p - 1, self.achievements_page + 1)
                            self.sfx.play("dash")

                # Boss Dialogue Mouse Click
                elif self.state == 'BOSS_DIALOGUE':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                        m_pos = event.pos
                        if self.dialogue_stage == 'QUESTION':
                            if self.dialogue_rects.get("opt1") and self.dialogue_rects["opt1"].collidepoint(m_pos):
                                self.handle_boss_dialogue_choice(1)
                            elif self.dialogue_rects.get("opt2") and self.dialogue_rects["opt2"].collidepoint(m_pos):
                                self.handle_boss_dialogue_choice(2)
                        elif self.dialogue_stage in ('ANSWER_LIED', 'ANSWER_NO_HIT', 'ANSWER_TRUTH'):
                            if self.dialogue_rects.get("btn_continue") and self.dialogue_rects["btn_continue"].collidepoint(m_pos):
                                self.close_boss_dialogue()

                # Perk Selection Mouse Click
                elif self.state == 'PERK_SELECTION':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                        card_w = 780
                        card_h = 122
                        card_x = VIEW_WIDTH // 2 - card_w // 2
                        card_y_start = 160
                        card_gap = 142
                        offerings = getattr(self, 'current_portal_offerings', [])
                        for idx in range(len(offerings)):
                            c_rect = pygame.Rect(card_x, card_y_start + idx * card_gap, card_w, card_h)
                            if c_rect.collidepoint(event.pos):
                                self.apply_perk(idx + 1)
                                break

                # Combo Forge Menu Mouse Drawing
                elif self.state == 'COMBO_FORGE_MENU':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button in (1, 3):
                            rects = self.get_combo_forge_rects()
                            if rects["btn_test"].collidepoint(event.pos):
                                if len(self.forge_slots) >= 3:
                                    resolved = COMBO_MATRIX.resolve_combo(self.forge_slots)
                                    self.fx.add_screen_shake(20.0)
                                    self.sfx.play("crit")
                                    self.forge_feedback = f"ТЕСТ: {resolved['name']} (Урон x{resolved['mult']:.2f})!"
                                else:
                                    self.forge_feedback = "Сначала начерти минимум 3 знака для комбо!"
                            elif rects["btn_seal"].collidepoint(event.pos):
                                if len(self.forge_slots) >= 3:
                                    resolved = COMBO_MATRIX.resolve_combo(self.forge_slots)
                                    self.sealed_ultra_combo = resolved
                                    self.sfx.play("crit")
                                    self.forge_feedback = f"★ УЛЬТРА-КОМБО «{resolved['name']}» ЗАПЕЧАТАНО В СЛОТ [F]!"
                                else:
                                    self.forge_feedback = "Нужно минимум 3 знака для запечатывания комбо!"
                            elif rects["btn_clear"].collidepoint(event.pos):
                                self.forge_slots.clear()
                                self.forge_feedback = "Слоты очищены. Начерти новую связку из 3-5 знаков!"
                            elif rects["btn_exit"].collidepoint(event.pos):
                                self.state = 'PLAYING'
                            else:
                                clicked_eid = None
                                for eid, er in rects["elem_rects"].items():
                                    if er.collidepoint(event.pos):
                                        clicked_eid = eid
                                        break
                                if clicked_eid:
                                    if COMBO_MATRIX.is_element_unlocked(clicked_eid):
                                        if len(self.forge_slots) < 5:
                                            self.forge_slots.append(clicked_eid)
                                            self.sfx.play("slash")
                                            if len(self.forge_slots) >= 3:
                                                res = COMBO_MATRIX.resolve_combo(self.forge_slots)
                                                self.forge_feedback = f"СИНТЕЗИРОВАНО: {res['name']}!"
                                            else:
                                                self.forge_feedback = f"Добавлена стихия: {ELEMENTS[clicked_eid]['name']} ({len(self.forge_slots)}/5)"
                                        else:
                                            self.forge_feedback = "Слоты заполнены (максимум 5 знаков)!"
                                    else:
                                        self.forge_feedback = f"Стихия засекречена! Достигни Этажа {ELEMENTS[clicked_eid]['floor_unlock']} для открытия."
                                        self.sfx.play("parry")
                                elif rects["canvas_rect"].collidepoint(event.pos):
                                    self.is_drawing = True
                                    self.forge_points = [event.pos]
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button in (1, 3) and self.is_drawing:
                            self.is_drawing = False
                            if len(self.forge_points) >= 3:
                                skill_id, score, tier, dev = evaluate_gesture(self.forge_points)
                                if skill_id and score >= 0.40:
                                    if len(self.forge_slots) < 5:
                                        self.forge_slots.append(skill_id)
                                        self.sfx.play("slash")
                                        if len(self.forge_slots) >= 3:
                                            res = COMBO_MATRIX.resolve_combo(self.forge_slots)
                                            self.forge_feedback = f"СИНТЕЗИРОВАНО: {res['name']}!"
                                        else:
                                            self.forge_feedback = f"Добавлен знак ({len(self.forge_slots)}/5). Черти дальше..."
                                else:
                                    self.forge_feedback = "Знак не распознан. Попробуй начертить четче!"
                            self.forge_points = []
                    elif event.type == pygame.MOUSEMOTION and self.is_drawing:
                        self.forge_points.append(event.pos)

                # Custom Glyph Studio Mouse Drawing
                elif self.state == 'CUSTOM_GLYPH_FORGE':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button in (1, 3):
                            self.is_drawing = True
                            self.custom_points = [event.pos]
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button in (1, 3):
                            self.is_drawing = False
                    elif event.type == pygame.MOUSEMOTION and self.is_drawing:
                        self.custom_points.append(event.pos)

                # Mouse Gesture Drawing
                elif self.state in ('PLAYING', 'DOJO'):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button in (1, 3):
                            self.is_drawing = True
                            self.stroke_points = [event.pos]

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button in (1, 3) and self.is_drawing:
                            self.is_drawing = False
                            if len(self.stroke_points) >= 2:
                                self.cast_gesture_ability(self.stroke_points)
                            self.stroke_points = []

                    elif event.type == pygame.MOUSEMOTION and self.is_drawing:
                        mx, my = event.pos
                        jitter = (self.current_mutator["jitter"] + getattr(self.player, 'bonus_jitter', 0.0)) if self.state != 'DOJO' else 0.0
                        if jitter > 0:
                            mx += random.uniform(-jitter, jitter)
                            my += random.uniform(-jitter, jitter)
                        self.stroke_points.append((mx, my))

            # -------------------------------------------------------------
            # UPDATE LOGIC
            # -------------------------------------------------------------
            if self.state in ('PLAYING', 'DOJO'):
                is_bullet_time = (self.bullet_time_timer > 0)
                if is_bullet_time:
                    self.bullet_time_timer = max(0.0, self.bullet_time_timer - real_dt)
                    sim_dt = real_dt * 0.20
                else:
                    sim_dt = real_dt

                self.anim_time += sim_dt
                keys = pygame.key.get_pressed()

                # Countdown timer (disabled in Dojo!)
                if self.state != 'DOJO':
                    if self.player.alive and self.zone_timer > 0:
                        self.zone_timer = max(0.0, self.zone_timer - sim_dt * self.current_mutator["timer_mult"] * getattr(self.player, 'timer_drain_mult', 1.0))
                        if self.zone_timer <= 0:
                            self.player.alive = False

                # Update entities
                self.player.update(sim_dt, keys, self.current_mutator["inertia_mult"], self.obstacles)

                # Camera lerp towards player
                target_cam_x = self.player.x - VIEW_WIDTH // 2
                target_cam_y = self.player.y - VIEW_HEIGHT // 2
                self.cam_x += (target_cam_x - self.cam_x) * 0.12
                self.cam_y += (target_cam_y - self.cam_y) * 0.12
                self.cam_x = max(0, min(MAP_WIDTH - VIEW_WIDTH, self.cam_x))
                self.cam_y = max(0, min(MAP_HEIGHT - VIEW_HEIGHT, self.cam_y))

                for ab in self.active_abilities:
                    ab.update(sim_dt, self.enemies, self.player, self.fx, self.sfx, self.art, self.obstacles)
                self.active_abilities = [ab for ab in self.active_abilities if ab.alive]

                for en in self.enemies:
                    en.update(sim_dt, self.player, self.fx, self.sfx, self.art, is_bullet_time, self.obstacles)

                # Enemy weapon drops loot roll
                for en in self.enemies:
                    if not en.alive and not getattr(en, 'loot_dropped', False):
                        en.loot_dropped = True
                        dropped_w = roll_enemy_weapon_drop(en, self.current_floor_idx)
                        if dropped_w:
                            dw_entity = DroppedWeapon(dropped_w, en.x + random.uniform(-14, 14), en.y + random.uniform(-14, 14))
                            self.dropped_weapons.append(dw_entity)
                            self.fx.spawn_sparks(en.x, en.y, dropped_w.glow_color, count=28, speed=220)
                            if dropped_w.tier == 5:
                                self.fx.add_screen_shake(18.0)
                                self.sfx.play("crit")
                                self.fx.add_floating_text("★★★ БОЖЕСТВЕННЫЙ ДАР (БЕЛОЕ СВЕЧЕНИЕ)! ★★★", en.x, en.y - 70, (255, 255, 255), size=28)
                            elif dropped_w.tier >= 3:
                                self.sfx.play("crit")
                                self.fx.add_floating_text(f"★ ВЫПАЛО: {dropped_w.name}! ★", en.x, en.y - 50, dropped_w.glow_color, size=24)
                            else:
                                self.sfx.play("parry")
                                self.fx.add_floating_text(f"ВЫПАЛО: {dropped_w.name}", en.x, en.y - 40, dropped_w.glow_color, size=20)

                # Update dropped weapons animation
                for dw in self.dropped_weapons:
                    dw.update(sim_dt)

                self.fx.update(sim_dt)

                # Wave & Portal Logic (Playing state only)
                if self.state == 'PLAYING':
                    alive_count = sum(1 for en in self.enemies if en.alive)
                    total_waves = len(self.current_floor_data["waves"])

                    if alive_count == 0 and not self.portal_active:
                        if not getattr(self.player, 'damage_taken_in_wave', False):
                            ACHIEVEMENT_MANAGER.unlock("flawless_wave", self.fx, self.sfx)

                        if self.current_wave_idx < total_waves - 1:
                            # Advance to next wave
                            self.spawn_wave(self.current_wave_idx + 1)
                        else:
                            # Floor completely cleared! Activate portal
                            self.portal_active = True
                            self.sfx.play("parry")
                            self.fx.add_floating_text("ЭТАЖ ЗАЧИЩЕН! ШАГНИ В ПОРТАЛ", self.portal_pos[0], self.portal_pos[1] - 50, TEXT_GOLD, size=32)

                    # Step into portal
                    if self.portal_active:
                        p_dist = math.hypot(self.player.x - self.portal_pos[0], self.player.y - self.portal_pos[1])
                        if p_dist < 46:
                            self.state = 'PERK_SELECTION'
                            diff = DIFFICULTY_MANAGER.current
                            only_c = CHALLENGE_MANAGER.should_offer_only_curses()
                            self.current_portal_offerings = generate_portal_offerings(
                                self.current_floor_idx + 1,
                                curse_chance=(1.0 if only_c else diff.curse_chance),
                                only_curses=only_c
                            )
                            self.sfx.play("crit")

            elif self.state in ('MAIN_MENU', 'DIFFICULTY_SELECT'):
                self.anim_time += real_dt
                update_menu_embers(real_dt, VIEW_WIDTH, VIEW_HEIGHT)
            else:
                self.anim_time += real_dt

            ACHIEVEMENT_MANAGER.update_popups(real_dt)

            # -------------------------------------------------------------
            # RENDERING
            # -------------------------------------------------------------
            fonts_dict = {
                "title": self.font_title,
                "large": self.font_large,
                "med": self.font_med,
                "small": self.font_small,
                "sym_large": self.font_sym_large,
                "sym_med": self.font_sym_med,
                "sym_small": self.font_sym_small
            }

            if self.state == 'MAIN_MENU':
                self.menu_buttons = draw_main_menu(self.screen, self.anim_time, fonts_dict, bg_image=self.art.title_menu_bg)
                ACHIEVEMENT_MANAGER.draw_active_popup(self.screen, self.anim_time, fonts_dict)
                pygame.display.flip()
                continue

            elif self.state == 'DIFFICULTY_SELECT':
                current_tab = getattr(self, 'diff_modal_tab', 0)
                self.diff_modal_rects = draw_difficulty_modal(self.screen, self.anim_time, fonts_dict, current_tab=current_tab)
                ACHIEVEMENT_MANAGER.draw_active_popup(self.screen, self.anim_time, fonts_dict)
                pygame.display.flip()
                continue

            elif self.state == 'ACHIEVEMENTS_MENU':
                self.ach_menu_rects = draw_achievements_screen(self.screen, self.anim_time, fonts_dict, scroll_page=self.achievements_page)
                ACHIEVEMENT_MANAGER.draw_active_popup(self.screen, self.anim_time, fonts_dict)
                pygame.display.flip()
                continue

            shake_x, shake_y = self.fx.get_shake_offset()
            off_x = -self.cam_x + shake_x
            off_y = -self.cam_y + shake_y

            # 1. Floor
            if self.art.tile_floor:
                tw, th = self.art.tile_floor.get_size()
                start_x = int((self.cam_x // tw) * tw)
                start_y = int((self.cam_y // th) * th)
                for tx in range(start_x, int(self.cam_x + VIEW_WIDTH + tw), tw):
                    for ty in range(start_y, int(self.cam_y + VIEW_HEIGHT + th), th):
                        self.screen.blit(self.art.tile_floor, (tx + off_x, ty + off_y))
            else:
                self.screen.fill((16, 20, 28))

            # Arena Boundaries
            pygame.draw.rect(self.screen, (55, 65, 95), (off_x + 40, off_y + 40, MAP_WIDTH - 80, MAP_HEIGHT - 80), 5)

            # 2. Obstacles (Pillars, Altars, Braziers)
            for obs in self.obstacles:
                draw_obstacle(self.screen, obs, off_x, off_y)

            # 3. Grimoire Lectern (Светящаяся книга)
            draw_grimoire_lectern(self.screen, self.lectern_pos[0], self.lectern_pos[1], self.anim_time, off_x, off_y)
            d_lect = math.hypot(self.player.x - self.lectern_pos[0], self.player.y - self.lectern_pos[1])
            if d_lect < 95:
                l_hint = self.font_small.render("[E] Открыть Гримуар Рецептов", True, TEXT_GOLD)
                self.screen.blit(l_hint, (int(self.lectern_pos[0] + off_x - l_hint.get_width() // 2), int(self.lectern_pos[1] + off_y - 48)))

            # 4. Portal if active
            if self.portal_active:
                draw_portal(self.screen, self.portal_pos[0] + off_x, self.portal_pos[1] + off_y, self.anim_time)

            # 5. Active Spells
            for ab in self.active_abilities:
                ab.draw(self.screen, off_x, off_y)

            # 6. Enemies
            for en in self.enemies:
                if not en.alive:
                    continue
                ex = int(en.x + off_x)
                ey = int(en.y + off_y)
                angle_to_player = math.atan2(self.player.y - en.y, self.player.x - en.x)

                draw_enemy_sprite(self.screen, self.art, en, ex, ey, self.anim_time, angle_to_player)

                # Enraged Boss Aura (If Judge of Truth was lied to)
                if getattr(en, 'enraged', False):
                    e_pulse = 0.5 + 0.5 * math.sin(self.anim_time * 10.0)
                    e_rad = en.radius + 18 + int(6 * e_pulse)
                    pygame.draw.circle(self.screen, (255, 45, 45), (ex, ey), e_rad, 3)
                    e_badge = self.font_small.render("[В ЯРОСТИ ОТ ЛЖИ: +25% СКОРОСТЬ]", True, (255, 75, 75))
                    self.screen.blit(e_badge, (ex - e_badge.get_width() // 2, ey - en.radius - 50))

                # Active Spell Immunities Barrier & Badge
                if getattr(en, 'spell_immunities', None) and len(en.spell_immunities) > 0:
                    hex_r = en.radius + 14 + int(3 * math.sin(self.anim_time * 8.0))
                    pygame.draw.circle(self.screen, (220, 90, 255), (ex, ey), hex_r, 2)
                    for i in range(6):
                        h_ang = self.anim_time * 2.5 + i * (math.pi / 3)
                        nx = ex + int(hex_r * math.cos(h_ang))
                        ny = ey + int(hex_r * math.sin(h_ang))
                        pygame.draw.circle(self.screen, (255, 180, 255), (nx, ny), 3)

                    imm_tags = ", ".join(en.spell_immunities.keys())
                    imm_badge = self.font_small.render(f"[ИММУНИТЕТ: {imm_tags}]", True, (245, 100, 255))
                    self.screen.blit(imm_badge, (ex - imm_badge.get_width() // 2, ey - en.radius - 34))

                # Backstab indicator
                if getattr(en, 'backstab_vulnerable', False):
                    pygame.draw.circle(self.screen, (255, 80, 240), (ex, ey - en.radius - 24), 8)
                    pygame.draw.circle(self.screen, (255, 255, 255), (ex, ey - en.radius - 24), 4)

                # Health Bar
                bar_w = int(48 * (1.0 + en.scale * 0.4))
                bar_h = 5
                hp_ratio = en.hp / en.max_hp
                pygame.draw.rect(self.screen, (20, 20, 25), (ex - bar_w // 2, ey - en.radius - 16, bar_w, bar_h))
                bar_col = (140, 230, 255) if getattr(en, 'is_frozen', False) else (230, 50, 50)
                pygame.draw.rect(self.screen, bar_col, (ex - bar_w // 2, ey - en.radius - 16, int(bar_w * hp_ratio), bar_h))

                # Windup telegraph
                if en.is_attacking:
                    ratio = min(1.0, en.windup_timer / (1.2 if en.scale > 1.4 else 0.85))
                    t_rad = int(en.radius + (45 if en.scale > 1.4 else 30) * ratio)
                    pygame.draw.circle(self.screen, (255, 50, 50), (ex, ey), t_rad, 2)

                lbl_text = en.name
                if getattr(en, 'is_frozen', False):
                    lbl_text = f"{en.name} [ЗАМОРОЖЕН x2.5]"
                elif getattr(en, 'backstab_vulnerable', False):
                    lbl_text = f"{en.name} [УЯЗВИМ x3]"
                lbl = self.font_small.render(lbl_text, True, en.tint)
                self.screen.blit(lbl, (ex - lbl.get_width() // 2, ey + en.radius + 6))

            # 6.5 Dropped Weapons on Arena Floor
            for dw in self.dropped_weapons:
                if dw.alive:
                    d_p = math.hypot(self.player.x - dw.x, self.player.y - dw.y)
                    is_near = (d_p < dw.pickup_radius)
                    dw.draw(self.screen, off_x, off_y, self.anim_time, fonts_dict, is_player_near=is_near, current_player_weapon=self.player.weapon)

            # 7. Player Character
            px = int(self.player.x + off_x)
            py = int(self.player.y + off_y)
            draw_player_character(
                self.screen, self.art, px, py, self.player.aim_angle, self.anim_time,
                self.player.weapon.color, self.player.fumble_timer > 0, self.player.i_frame_timer > 0,
                weapon_tier=self.player.weapon.tier
            )

            # Bullet-Time Barrier
            if self.bullet_time_timer > 0:
                shield_r = int(38 + 4 * math.sin(self.anim_time * 12))
                shield_surf = pygame.Surface((shield_r * 2 + 10, shield_r * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(shield_surf, (255, 215, 60, 160), (shield_r + 5, shield_r + 5), shield_r, 3)
                pygame.draw.circle(shield_surf, (255, 245, 180, 80), (shield_r + 5, shield_r + 5), shield_r - 6)
                self.screen.blit(shield_surf, (px - shield_r - 5, py - shield_r - 5))

            # 8. Slashes & Particles
            self.fx.draw(self.screen, off_x, off_y)

            # 9. Live Gesture Ink
            if self.is_drawing and len(self.stroke_points) >= 2:
                pygame.draw.lines(self.screen, (80, 160, 255), False, self.stroke_points, width=7)
                pygame.draw.lines(self.screen, (255, 255, 255), False, self.stroke_points, width=2)
                tip_x, tip_y = self.stroke_points[-1]
                pygame.draw.circle(self.screen, (255, 255, 220), (tip_x, tip_y), 6)

            # 10. Dynamic Lighting Overlay
            base_light_r = 250 if self.bullet_time_timer <= 0 else 320
            p_light_r = CHALLENGE_MANAGER.get_light_radius(base_light_r)
            if getattr(self.player.weapon, 'tier', 1) == 5:
                p_light_r = max(p_light_r, 340)
                p_light_col = (255, 255, 255)
            else:
                p_light_col = (140, 180, 255) if self.bullet_time_timer <= 0 else (255, 220, 80)

            light_sources = [
                (self.player.x + off_x, self.player.y + off_y, p_light_r, p_light_col, 0.95),
                (self.lectern_pos[0] + off_x, self.lectern_pos[1] + off_y, 140, (120, 220, 255), 0.8)
            ]
            if self.portal_active:
                light_sources.append((self.portal_pos[0] + off_x, self.portal_pos[1] + off_y, 200, (100, 220, 255), 0.9))
            for obs in self.obstacles:
                if obs['type'] == 'BRAZIER':
                    light_sources.append((obs['x'] + off_x, obs['y'] + off_y, 160, (255, 140, 40), 0.75))
            for ab in self.active_abilities:
                l = ab.get_light()
                if l:
                    light_sources.append((l[0] + off_x, l[1] + off_y, l[2], l[3], l[4]))
            for en in self.enemies:
                if en.alive and en.scale > 1.3:
                    light_sources.append((en.x + off_x, en.y + off_y, int(120 * en.scale), en.tint, 0.65))

            # Dropped weapons dynamic lighting
            for dw in self.dropped_weapons:
                if dw.alive:
                    l = dw.get_light()
                    light_sources.append((l[0] + off_x, l[1] + off_y, l[2], l[3], l[4]))

            self.art.render_lighting(self.screen, light_sources)

            # -------------------------------------------------------------
            # HUD RENDERING
            # -------------------------------------------------------------
            # Top Banner: Survival Countdown & Floor Info
            f_data = self.current_floor_data
            if self.state == 'DOJO':
                mode_surf = self.font_large.render("ТРЕНИРОВОЧНЫЙ ЗАЛ (ДОДЗЁ) — БЕСКОНЕЧНЫЙ ТАЙМЕР [T / ESC ВЫХОД]", True, TEXT_CYAN)
                self.screen.blit(mode_surf, (VIEW_WIDTH // 2 - mode_surf.get_width() // 2, 12))
            else:
                timer_color = TEXT_WHITE if self.zone_timer > 15 else TEXT_RED
                mins = int(self.zone_timer) // 60
                secs = self.zone_timer % 60
                timer_str = f"ТАЙМЕР: {mins:02d}:{secs:05.2f}"
                timer_surf = self.font_large.render(timer_str, True, timer_color)
                self.screen.blit(timer_surf, (VIEW_WIDTH // 2 - timer_surf.get_width() // 2, 10))

                # Wave Counter Badge
                total_w = len(f_data["waves"])
                cur_w = self.current_wave_idx + 1
                alive_c = sum(1 for en in self.enemies if en.alive)
                wave_txt = f"Этаж {f_data['floor']}: {f_data['name']} | ВОЛНА {cur_w}/{total_w} (Врагов: {alive_c})"
                wave_surf = self.font_med.render(wave_txt, True, TEXT_GOLD)
                self.screen.blit(wave_surf, (VIEW_WIDTH // 2 - wave_surf.get_width() // 2, 38))

            # Grand Boss Health Bar for Floor 50 Boss (Верховный Судия Истины)
            judge_boss = next((en for en in self.enemies if en.alive and en.id == "judge_of_truth"), None)
            if judge_boss:
                b_bar_w = 660
                b_bar_h = 24
                bx = VIEW_WIDTH // 2 - b_bar_w // 2
                by = 64
                pygame.draw.rect(self.screen, (15, 18, 28), (bx, by, b_bar_w, b_bar_h), border_radius=4)
                ratio = max(0.0, min(1.0, judge_boss.hp / judge_boss.max_hp))
                b_col = (255, 60, 60) if getattr(judge_boss, 'enraged', False) else (255, 215, 60)
                pygame.draw.rect(self.screen, b_col, (bx, by, int(b_bar_w * ratio), b_bar_h), border_radius=4)
                pygame.draw.rect(self.screen, (255, 230, 100), (bx, by, b_bar_w, b_bar_h), 2, border_radius=4)

                b_status = " [В ЯРОСТИ ОТ ЛЖИ: +25% SPD]" if getattr(judge_boss, 'enraged', False) else ""
                sym_s = self.font_sym_med.render("⚖", True, (255, 220, 80))
                boss_txt = self.font_med.render(f" ВЕРХОВНЫЙ СУДИЯ ИСТИНЫ{b_status}  HP: {int(judge_boss.hp)} / {judge_boss.max_hp} ", True, (255, 255, 255))
                tot_w = sym_s.get_width() * 2 + boss_txt.get_width()
                start_x = VIEW_WIDTH // 2 - tot_w // 2
                self.screen.blit(sym_s, (start_x, by + 3))
                self.screen.blit(boss_txt, (start_x + sym_s.get_width(), by + 3))
                self.screen.blit(sym_s, (start_x + sym_s.get_width() + boss_txt.get_width(), by + 3))

            # Bullet Time Banner
            if self.bullet_time_timer > 0:
                bt_str = f"⚡ SLO-MO x5: {self.bullet_time_timer:.1f}s ⚡"
                bt_surf = self.font_med.render(bt_str, True, TEXT_GOLD)
                banner_rect = pygame.Rect(VIEW_WIDTH // 2 - bt_surf.get_width() // 2 - 12, 64, bt_surf.get_width() + 24, 26)
                pygame.draw.rect(self.screen, (20, 20, 10, 220), banner_rect)
                pygame.draw.rect(self.screen, TEXT_GOLD, banner_rect, 2)
                self.screen.blit(bt_surf, (VIEW_WIDTH // 2 - bt_surf.get_width() // 2, 66))

            # Mutator Badge (Top Right)
            if self.state != 'DOJO':
                mut = self.current_mutator
                mut_surf = self.font_med.render(f"Аномалия: {mut['name']}", True, mut['color'])
                self.screen.blit(mut_surf, (VIEW_WIDTH - mut_surf.get_width() - 35, 12))
            
            pause_hint = self.font_small.render("[C] АЛТАРЬ КОМБО  [F] ВЫЗОВ КОМБО  [T] ДОДЗЁ  [K] СВОЙ ЗНАК  [ESC] ПАУЗА", True, (190, 200, 220))
            self.screen.blit(pause_hint, (VIEW_WIDTH - pause_hint.get_width() - 35, 36))

            if self.sealed_ultra_combo:
                sc_txt = f"★ [F] ЗАПЕЧАТАНО: {self.sealed_ultra_combo['name']}"
                sc_surf = self.font_small.render(sc_txt, True, self.sealed_ultra_combo['color'])
                self.screen.blit(sc_surf, (VIEW_WIDTH - sc_surf.get_width() - 35, 58))

            # Player Health & Weapon (Top Left)
            pygame.draw.rect(self.screen, (30, 32, 44), (35, 14, 210, 16))
            hp_w = int(210 * (self.player.hp / self.player.max_hp))
            pygame.draw.rect(self.screen, (60, 225, 95), (35, 14, hp_w, 16))
            hp_txt = self.font_small.render(f"HP: {int(self.player.hp)} / {self.player.max_hp}", True, TEXT_WHITE)
            self.screen.blit(hp_txt, (45, 14))

            diff = DIFFICULTY_MANAGER.current
            diff_h = self.font_small.render(f"{diff.badge}", True, diff.color)
            self.screen.blit(diff_h, (255, 14))

            ch_active = CHALLENGE_MANAGER.get_active_count()
            if ch_active > 0:
                ch_badge = self.font_small.render(f"+ ☠ {ch_active} УСЛОЖН.", True, (255, 85, 100))
                self.screen.blit(ch_badge, (255 + diff_h.get_width() + 10, 14))

            # 3-Slot Weapon Belt in HUD
            cur_slot = getattr(self.player, 'active_weapon_slot', 1)
            slots_x = 35
            slots_y = 36
            slot_w = 118
            slot_h = 22
            slot_gap = 6

            for s_idx in (1, 2, 3):
                s_rect = pygame.Rect(slots_x + (s_idx - 1) * (slot_w + slot_gap), slots_y, slot_w, slot_h)
                s_wep = self.player.weapon_slots.get(s_idx, self.player.weapon)
                is_active_s = (s_idx == cur_slot)

                # Slot background
                bg_c = (35, 40, 58) if is_active_s else (16, 20, 30)
                pygame.draw.rect(self.screen, bg_c, s_rect, border_radius=3)
                
                # Slot border
                bdr_c = (255, 255, 255) if (is_active_s and s_wep.tier == 5) else (s_wep.glow_color if is_active_s else (55, 65, 85))
                bdr_w = 2 if is_active_s else 1
                pygame.draw.rect(self.screen, bdr_c, s_rect, bdr_w, border_radius=3)

                # Key Badge & Name
                k_txt = f"[{s_idx}] "
                k_s = self.font_small.render(k_txt, True, TEXT_GOLD if is_active_s else (150, 160, 180))
                
                clean_name = s_wep.name.replace("«", "").replace("»", "")
                if len(clean_name) > 8:
                    clean_name = clean_name[:7] + ".."
                w_s = self.font_small.render(clean_name, True, s_wep.glow_color)
                
                self.screen.blit(k_s, (s_rect.x + 4, s_rect.y + 3))
                self.screen.blit(w_s, (s_rect.x + 4 + k_s.get_width(), s_rect.y + 3))

            # Active Weapon Detailed Status Line
            act_w = self.player.weapon
            w_info = f"{act_w.name}  |  {act_w.short_tier}  |  УРОН x{act_w.damage_mult:.2f}  |  {act_w.weight} кг"
            w_info_s = self.font_small.render(w_info, True, act_w.glow_color)
            self.screen.blit(w_info_s, (35, slots_y + slot_h + 4))

            # Special Perk / Tier status line
            status_y = slots_y + slot_h + 20
            if act_w.tier == 5:
                t5_s = self.font_small.render("[БОЖЕСТВЕННЫЙ РАНГ]", True, (255, 255, 255))
                self.screen.blit(t5_s, (35, status_y))
                status_y += 18
            if act_w.perk_desc:
                p_s = self.font_small.render(f"Свойство: {act_w.perk_desc}", True, (240, 220, 130))
                self.screen.blit(p_s, (35, status_y))
                status_y += 18

            if getattr(self.player, 'curse_count', 0) > 0:
                c_txt = f"☠ ПРОКЛЯТИЙ: {self.player.curse_count}"
                c_surf = self.font_small.render(c_txt, True, (230, 90, 255))
                self.screen.blit(c_surf, (35, status_y))
                status_y += 18

            if self.player.combo_count > 0:
                mult = 1.0 + (self.player.combo_count - 1) * 0.30
                combo_surf = self.font_large.render(f"СЕРИЯ x{self.player.combo_count}! (УРОН x{mult:.2f})", True, TEXT_GOLD)
                self.screen.blit(combo_surf, (35, status_y))

            # Bottom Panel: Grimoire & Synthesis Recipes
            bottom_y = VIEW_HEIGHT - 105
            pygame.draw.rect(self.screen, (10, 12, 18), (0, bottom_y, VIEW_WIDTH, 105))
            pygame.draw.line(self.screen, (35, 45, 68), (0, bottom_y), (VIEW_WIDTH, bottom_y), 2)

            # Left side: Synthesis Combos
            synth_banner = self.font_small.render("СИНТЕЗ ЗАКЛИНАНИЙ (ЧЕРТИ ДВА ЗНАКА СВЯЗКОЙ) | [K] — НАРИСОВАТЬ СВОЙ ЗНАК:", True, TEXT_GOLD)
            self.screen.blit(synth_banner, (30, bottom_y + 8))

            fusions_hud = [
                ("[|] + [V]", "Крио-Метеорит", (140, 230, 255), "Заморозка по области!"),
                ("[O] + [^]", "Инферно-Воронка", (255, 140, 30), "Черная дыра в огне!"),
                ("[X] + [—]", "Пространство", (140, 240, 255), "Световые трещины!"),
                ("[🛡] + [⌛]", "Хроно-Стазис", (210, 100, 255), "Полная остановка времени!")
            ]
            fx_pos = 30
            for code, fname, fcol, fdesc in fusions_hud:
                c_s = self.font_med.render(f"{code} {fname}", True, fcol)
                self.screen.blit(c_s, (fx_pos, bottom_y + 30))
                d_s = self.font_small.render(fdesc, True, (180, 190, 210))
                self.screen.blit(d_s, (fx_pos, bottom_y + 58))
                fx_pos += 210

            # Live Accuracy Feedback Box
            if self.last_accuracy_info:
                info = self.last_accuracy_info
                box_x = VIEW_WIDTH - 145
                acc_title = self.font_small.render(f"{info['name']}", True, info['color'])
                self.screen.blit(acc_title, (box_x, bottom_y + 10))
                tier_color = TEXT_GOLD if info['tier'] == "PERFECT" else (TEXT_CYAN if info['tier'] == "CLEAN" else TEXT_RED)
                acc_val = self.font_med.render(f"{info['score']}% [{info['tier']}]", True, tier_color)
                self.screen.blit(acc_val, (box_x, bottom_y + 32))

            # -------------------------------------------------------------
            # OVERLAYS: TOME OF SYNTHESIS, PAUSE, PERK SELECTION, DEATH
            # -------------------------------------------------------------
            # TOME OF SYNTHESIS (INTERACTIVE SPELLBOOK ALTAR)
            if self.state == 'TOME_OF_SYNTHESIS':
                overlay = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 10, 16, 240))
                self.screen.blit(overlay, (0, 0))

                tome_rect = pygame.Rect(VIEW_WIDTH // 2 - 460, 60, 920, 680)
                pygame.draw.rect(self.screen, (20, 24, 38), tome_rect)
                pygame.draw.rect(self.screen, (60, 90, 140), tome_rect, 3)

                t_title = self.font_title.render("📖 ДРЕВНИЙ ГРИМУАР СИНТЕЗА КОМБО", True, TEXT_GOLD)
                self.screen.blit(t_title, (tome_rect.centerx - t_title.get_width() // 2, 85))

                sub_t = self.font_med.render("Соединяй знаки подряд в течение 1.5 сек для получения сверх-заклинаний:", True, TEXT_WHITE)
                self.screen.blit(sub_t, (tome_rect.centerx - sub_t.get_width() // 2, 135))

                recipes = [
                    ("❄ КРИО-МЕТЕОРИТ [| + V]", "Черти Метеор (|), затем сразу Ледяной знак (V).", "Метеорит обрушивается на арену и ВЫЗЫВАЕТ ВОЛНУ ЗАМОРОЗКИ по площади!", (140, 230, 255)),
                    ("🔥 ОГНЕННЫЙ КОЛЛАПС [O + ^]", "Черти Черную дыру (O), затем сразу Инферно (^).", "Сингулярность воспламеняется, сжигая монстров и детонируя взрывом сверхновой!", (255, 140, 30)),
                    ("🌌 ПРОСТРАНСТВЕННЫЙ РАЗРЫВ [X + —]", "Черти Крест (X), затем сразу Срез (—).", "Рассекает экран световыми трещинами по диагоналям и горизонтали арены (+155% урона)!", (140, 240, 255)),
                    ("⏳ АБСОЛЮТНЫЙ ХРОНО-СТАЗИС [🛡 + ⌛]", "Черти Щит (🛡), затем сразу Песочные часы (⌛).", "Полная остановка времени на 4.5 секунды! Все враги и боссы замирают на месте!", (210, 100, 255)),
                    ("☀ СВЕТОВОЙ КАТАКЛИЗМ [△ + ★]", "Черти Призму (△), затем сразу Звезду (★).", "Ослепляющая божественная вспышка на всю арену, детонирующая нежить и порождения тьмы!", (255, 255, 180))
                ]

                ry = 165
                for r_head, r_how, r_eff, r_col in recipes:
                    pygame.draw.rect(self.screen, (28, 34, 52), (tome_rect.x + 30, ry, tome_rect.width - 60, 88))
                    pygame.draw.rect(self.screen, r_col, (tome_rect.x + 30, ry, tome_rect.width - 60, 88), 1)

                    h_s = self.font_med.render(r_head, True, r_col)
                    self.screen.blit(h_s, (tome_rect.x + 45, ry + 8))
                    hw_s = self.font_small.render(f"Как начертить: {r_how}", True, TEXT_GOLD)
                    self.screen.blit(hw_s, (tome_rect.x + 45, ry + 34))
                    ef_s = self.font_small.render(f"Эффект: {r_eff}", True, (210, 220, 240))
                    self.screen.blit(ef_s, (tome_rect.x + 45, ry + 58))

                    ry += 98

                exit_h = self.font_med.render("Нажми [ESC] или [E], чтобы закрыть книгу и вернуться в бой", True, (160, 180, 200))
                self.screen.blit(exit_h, (tome_rect.centerx - exit_h.get_width() // 2, ry + 10))

            # COMBO FORGE MENU (17 ELEMENTS & 204 SYNTHESIS MATRIX)
            elif self.state == 'COMBO_FORGE_MENU':
                self._draw_combo_forge_menu()

            # CUSTOM GLYPH FORGE (DRAW YOUR OWN RUNE)
            elif self.state == 'CUSTOM_GLYPH_FORGE':
                overlay = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 10, 18, 245))
                self.screen.blit(overlay, (0, 0))

                title = self.font_title.render("✦ КУЗНИЦА СВОИХ ЗНАКОВ (CUSTOM GLYPH STUDIO) ✦", True, TEXT_GOLD)
                self.screen.blit(title, (VIEW_WIDTH // 2 - title.get_width() // 2, 40))

                sub1 = self.font_med.render("Зажми ЛКМ/ПКМ и нарисуй В СВОБОДНОЙ ФОРМЕ любой свой знак комбо!", True, TEXT_WHITE)
                self.screen.blit(sub1, (VIEW_WIDTH // 2 - sub1.get_width() // 2, 85))

                # Canvas drawing box in center
                box_w, box_h = 480, 480
                box_x = VIEW_WIDTH // 2 - box_w // 2
                box_y = 125
                canvas_rect = pygame.Rect(box_x, box_y, box_w, box_h)
                pygame.draw.rect(self.screen, (16, 20, 32), canvas_rect)
                pygame.draw.rect(self.screen, (255, 220, 80), canvas_rect, 3)

                # Crosshair guides inside canvas
                pygame.draw.line(self.screen, (35, 45, 68), (box_x, box_y + box_h // 2), (box_x + box_w, box_y + box_h // 2), 1)
                pygame.draw.line(self.screen, (35, 45, 68), (box_x + box_w // 2, box_y), (box_x + box_w // 2, box_y + box_h), 1)
                pygame.draw.circle(self.screen, (45, 55, 85), (box_x + box_w // 2, box_y + box_h // 2), 140, 1)

                # Render user's drawn custom stroke points
                if len(self.custom_points) > 1:
                    pygame.draw.lines(self.screen, (255, 235, 90), False, self.custom_points, 6)
                    pygame.draw.lines(self.screen, (255, 255, 255), False, self.custom_points, 2)
                    for pt in self.custom_points:
                        pygame.draw.circle(self.screen, (255, 200, 50), pt, 4)

                # Status / Feedback text
                fb_col = TEXT_GOLD if "СОХРАНЕН" in self.custom_glyph_feedback else TEXT_CYAN
                fb_surf = self.font_large.render(self.custom_glyph_feedback, True, fb_col)
                self.screen.blit(fb_surf, (VIEW_WIDTH // 2 - fb_surf.get_width() // 2, box_y + box_h + 20))

                controls_surf = self.font_med.render("[ENTER] — Сохранить знак в память  |  [BACKSPACE] — Очистить  |  [ESC / K] — Назад в игру", True, (180, 195, 220))
                self.screen.blit(controls_surf, (VIEW_WIDTH // 2 - controls_surf.get_width() // 2, box_y + box_h + 55))

            # PAUSE MENU
            elif self.state == 'PAUSED':
                overlay = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((6, 8, 14, 235))
                self.screen.blit(overlay, (0, 0))

                title = self.font_title.render("ПАУЗА В ИГРЕ", True, TEXT_GOLD)
                self.screen.blit(title, (VIEW_WIDTH // 2 - title.get_width() // 2, 80))

                opts = [
                    "[ESC / P] — Продолжить бой",
                    "[F5] — Тест: Прыжок на 50-й этаж к Боссу Истины",
                    "[F6] — Тест: Получить 20 урона  |  [F7] — Сбросить урон (0 HP No-Hit)",
                    "[T] — Войти в Тренировочный Зал (Додзё)  |  [K] — Кузница Своих Знаков",
                    "[R] — Начать забег заново  |  [M] — Главное Меню  |  [Q] — Выйти из игры"
                ]
                oy = 135
                for opt in opts:
                    s = self.font_med.render(opt, True, TEXT_GOLD if "[F5]" in opt else TEXT_WHITE)
                    self.screen.blit(s, (VIEW_WIDTH // 2 - s.get_width() // 2, oy))
                    oy += 32

                guide_rect = pygame.Rect(VIEW_WIDTH // 2 - 470, 315, 940, 440)
                pygame.draw.rect(self.screen, (15, 20, 32), guide_rect)
                pygame.draw.rect(self.screen, (45, 60, 90), guide_rect, 2)

                gt_surf = self.font_large.render("ГРИМУАР СМЕРТЕЛЬНОГО ЧЕРЧЕНИЯ", True, TEXT_CYAN)
                self.screen.blit(gt_surf, (guide_rect.centerx - gt_surf.get_width() // 2, 325))

                grimoire_entries = [
                    ("🛡 Блок Бастиона:", "Контур щита. Блокирует урон и включает Slo-Mo в 5 раз!"),
                    ("⌛ Теневая Рокировка:", "Песочные часы. Меняет местами тебя и врага (BACKSTAB +200%)!"),
                    ("★ Звезда Катаклизма:", "Пятиконечная звезда. Орбитальный взрыв на всю арену +15s таймера!"),
                    ("⚔ Крестовой Разруб [X]:", "Крест 'X'. Пробивает броню и наносит двойной критический урон!"),
                    ("△ Эгида Призмы [△]:", "Треугольник. Призматический щит, отбрасывающий врагов."),
                    ("∞ Петля Омнислеш [∞]:", "Восьмерка / Петля. Шквал из 10 фантомных клинковых срезов!"),
                    ("✦ Твой Знак Владыки [✦]:", "Собственный знак из Кузницы [K]! Сверхкритический урон x3!"),
                    ("❄ Крио-Метеорит [| + V]:", "СИНТЕЗ: Метеор + Лед => Метеорит с ЗАМОРОЗКОЙ ВСЕХ ВРАГОВ ПО ОБЛАСТИ!"),
                    ("🔥 Инферно-Коллапс [O + ^]:", "СИНТЕЗ: Черная дыра + Огонь => Пылающая гравитационная воронка!"),
                    ("🌌 Пространство [X + —]:", "СИНТЕЗ: Крест + Срез => Световые трещины по всей арене!"),
                    ("⏳ Хроно-Стазис [🛡 + ⌛]:", "СИНТЕЗ: Щит + Часы => Полная остановка времени на 4.5 сек!")
                ]
                gy = 358
                for sym, desc in grimoire_entries:
                    s1 = self.font_med.render(sym, True, TEXT_GOLD)
                    self.screen.blit(s1, (guide_rect.x + 25, gy))
                    s2 = self.font_small.render(desc, True, (210, 220, 240))
                    self.screen.blit(s2, (guide_rect.x + 270, gy + 3))
                    gy += 32

            # PERK SELECTION
            elif self.state == 'PERK_SELECTION':
                overlay = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 12, 20, 245))
                self.screen.blit(overlay, (0, 0))

                fl_win = self.font_title.render(f"ЭТАЖ {self.current_floor_data['floor']} ЗАЧИЩЕН!", True, TEXT_GOLD)
                self.screen.blit(fl_win, (VIEW_WIDTH // 2 - fl_win.get_width() // 2, 55))

                if CHALLENGE_MANAGER.should_offer_only_curses():
                    sub = self.font_large.render("☠ ЧЕРТОГ ЧИСТИЛИЩА: ТОЛЬКО ДЕБАФФЫ (0 БАФФОВ)! ☠", True, (255, 90, 130))
                else:
                    sub = self.font_large.render("ВРАТА БЕЗДНЫ: ВЫБЕРИ ДВУЕДИНЫЙ ПАКТ ИЛИ ПРОКЛЯТЫЙ ДАР:", True, TEXT_WHITE)
                self.screen.blit(sub, (VIEW_WIDTH // 2 - sub.get_width() // 2, 102))

                fonts_dict = {
                    "large": self.font_large,
                    "med": self.font_med,
                    "small": self.font_small,
                    "sym_large": self.font_sym_large,
                    "sym_med": self.font_sym_med,
                    "sym_small": self.font_sym_small
                }

                card_w = 780
                card_h = 124
                card_x = VIEW_WIDTH // 2 - card_w // 2
                card_y_start = 150
                card_gap = 144
                m_pos = pygame.mouse.get_pos()

                offerings = getattr(self, 'current_portal_offerings', [])
                for idx, offering in enumerate(offerings):
                    c_rect = pygame.Rect(card_x, card_y_start + idx * card_gap, card_w, card_h)
                    is_hov = c_rect.collidepoint(m_pos)

                    if offering.is_cursed:
                        draw_cracked_cursed_card(self.screen, c_rect, offering, self.anim_time, is_hov, fonts_dict)
                    else:
                        draw_double_edged_card(self.screen, c_rect, offering, self.anim_time, is_hov, fonts_dict)

                    # Shortcut Key Badge in top right corner
                    badge_rect = pygame.Rect(c_rect.right - 58, c_rect.y + 12, 44, 30)
                    badge_col = (230, 100, 255) if offering.is_cursed else TEXT_GOLD
                    pygame.draw.rect(self.screen, (12, 14, 22), badge_rect)
                    pygame.draw.rect(self.screen, badge_col, badge_rect, 2)
                    k_surf = self.font_large.render(f"[{idx + 1}]", True, badge_col)
                    self.screen.blit(k_surf, (badge_rect.centerx - k_surf.get_width() // 2, badge_rect.centery - k_surf.get_height() // 2))

                hint = self.font_med.render("Нажми клавишу [1], [2] или [3] на клавиатуре, либо нажми ЛКМ по карточке", True, (170, 190, 215))
                self.screen.blit(hint, (VIEW_WIDTH // 2 - hint.get_width() // 2, 600))

                if CHALLENGE_MANAGER.should_offer_only_curses():
                    c_badge = self.font_med.render("☠ АКТИВНО УСЛОЖНЕНИЕ «ТОЛЬКО ДЕБАФФЫ» — ПОРТАЛ ПРЕДЛАГАЕТ ЛИШЬ ПРОКЛЯТИЯ! ☠", True, (255, 80, 120))
                    self.screen.blit(c_badge, (VIEW_WIDTH // 2 - c_badge.get_width() // 2, 632))
                elif getattr(self.player, 'curse_count', 0) > 0:
                    c_badge = self.font_med.render(f"☠ НАКОПЛЕННЫЕ ПРОКЛЯТИЯ БЕЗДНЫ: {self.player.curse_count} (Суммарные дебаффы активны) ☠", True, (240, 90, 255))
                    self.screen.blit(c_badge, (VIEW_WIDTH // 2 - c_badge.get_width() // 2, 632))

            # BOSS DIALOGUE OVERLAY (Level 50 Encounter)
            elif self.state == 'BOSS_DIALOGUE':
                self.draw_boss_dialogue(self.screen, self.anim_time, fonts_dict)

            # PERMADEATH OVERLAY
            elif not self.player.alive:
                overlay = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 10, 16, 225))
                self.screen.blit(overlay, (0, 0))

                death_msg = "ВРЕМЯ ИСТЕКЛО" if self.zone_timer <= 0 else "ТЫ ПАЛ (PERMADEATH)"
                death_surf = self.font_title.render(death_msg, True, TEXT_RED)
                self.screen.blit(death_surf, (VIEW_WIDTH // 2 - death_surf.get_width() // 2, VIEW_HEIGHT // 2 - 50))

                score_surf = self.font_large.render(f"Достигнут Этаж: {self.current_floor_data['floor']}", True, TEXT_GOLD)
                self.screen.blit(score_surf, (VIEW_WIDTH // 2 - score_surf.get_width() // 2, VIEW_HEIGHT // 2 + 5))

                sub_surf = self.font_med.render("Нажми [R] — начать заново  |  [M] — Главное Меню", True, TEXT_WHITE)
                self.screen.blit(sub_surf, (VIEW_WIDTH // 2 - sub_surf.get_width() // 2, VIEW_HEIGHT // 2 + 50))

            ACHIEVEMENT_MANAGER.draw_active_popup(self.screen, self.anim_time, fonts_dict)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
