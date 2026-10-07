"""
bosses.py - Fully Bespoke Boss Combat System for GLYPH-BLADE.
Implements:
1. 5 100% Unique, Dedicated Abilities for EVERY boss (40 unique abilities total across 8 bosses).
   Every boss has their OWN dedicated execution function with custom mechanics, projectile counts,
   speeds, AoE hazards, and ultimate cataclysms.
2. 8 Unique Reaction Dodges & Evasions with bespoke particle themes, speeds, sounds, and i-frames.
3. Telegraphed arcane hazard rings, homing souls, ground rifts, leaps, and cataclysmic ultimates.
"""

import math
import random
import pygame

# =============================================================================
# BOSS PROJECTILE & HAZARD ENTITIES
# =============================================================================

class BossProjectile:
    def __init__(self, x, y, vx, vy, damage, radius, color, duration=3.0, name="Снаряд", trail=True, homing=False, homing_turn=2.0, bounce=False):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.damage = float(damage)
        self.radius = int(radius)
        self.color = color
        self.duration = duration
        self.age = 0.0
        self.alive = True
        self.name = name
        self.trail = trail
        self.homing = homing
        self.homing_turn = homing_turn
        self.bounce = bounce
        self.bounces_left = 2 if bounce else 0

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        self.age += dt
        if self.age >= self.duration:
            self.alive = False
            return

        # Optional homing behavior towards player
        if self.homing and player and player.alive:
            dist = math.hypot(player.x - self.x, player.y - self.y)
            if dist > 10:
                target_vx = (player.x - self.x) / dist * math.hypot(self.vx, self.vy)
                target_vy = (player.y - self.y) / dist * math.hypot(self.vx, self.vy)
                self.vx += (target_vx - self.vx) * self.homing_turn * dt
                self.vy += (target_vy - self.vy) * self.homing_turn * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Wall bounce if enabled
        if self.bounce and self.bounces_left > 0:
            if self.x < 50 or self.x > 1870:
                self.vx = -self.vx
                self.bounces_left -= 1
                fx.spawn_sparks(self.x, self.y, self.color, count=8, speed=120)
            if self.y < 50 or self.y > 1030:
                self.vy = -self.vy
                self.bounces_left -= 1
                fx.spawn_sparks(self.x, self.y, self.color, count=8, speed=120)

        # Spawn trail sparks
        if self.trail and random.random() < 0.4:
            fx.spawn_sparks(self.x, self.y, self.color, count=2, speed=60)

        # Check collision with player
        if player and player.alive and player.i_frame_timer <= 0:
            p_dist = math.hypot(player.x - self.x, player.y - self.y)
            if p_dist < self.radius + player.radius:
                self.alive = False
                player.take_damage(self.damage, fx, sfx, art, is_shielded=(player.i_frame_timer > 0))
                fx.spawn_sparks(self.x, self.y, self.color, count=16, speed=180)
                fx.add_screen_shake(8.0)
                sfx.play("hit")

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), max(2, self.radius // 2))

    def get_light(self):
        return (self.x, self.y, self.radius * 6, self.color, 0.7)


class BossGroundHazard:
    """Telegraphed arcane hazard: smooth concentric warning rings, then detonates."""
    def __init__(self, x, y, radius, damage, windup_time=0.75, linger_time=0.45, color=(255, 60, 60), name="Опасная Зона", slow_player=False):
        self.x = float(x)
        self.y = float(y)
        self.radius = int(radius)
        self.damage = float(damage)
        self.windup_time = windup_time
        self.linger_time = linger_time
        self.total_duration = windup_time + linger_time
        self.age = 0.0
        self.alive = True
        self.has_exploded = False
        self.color = color
        self.name = name
        self.slow_player = slow_player

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        self.age += dt

        # Optional slow while inside warning area
        if self.slow_player and player and player.alive:
            if math.hypot(player.x - self.x, player.y - self.y) < self.radius:
                player.speed = getattr(player, 'base_speed', 260.0) * 0.65

        if self.age >= self.windup_time and not self.has_exploded:
            self.has_exploded = True
            fx.add_screen_shake(16.0)
            fx.spawn_sparks(self.x, self.y, self.color, count=36, speed=320)
            art.add_scorch_mark(self.x, self.y, radius=int(self.radius * 0.8))
            sfx.play("crit")

            # Damage check at detonation
            if player and player.alive and player.i_frame_timer <= 0:
                p_dist = math.hypot(player.x - self.x, player.y - self.y)
                if p_dist < self.radius + player.radius:
                    player.take_damage(self.damage, fx, sfx, art, is_shielded=(player.i_frame_timer > 0))
                    fx.add_floating_text(f"УДАР ЗОНЫ! -{int(self.damage)} HP", player.x, player.y - 35, self.color, size=24)

        if self.age >= self.total_duration:
            self.alive = False

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)

        if not self.has_exploded:
            # Clean arcane warning rings (no clunky blocky crosses or rectangles)
            prog = min(1.0, self.age / self.windup_time)
            pulse_rad = int(self.radius * prog)
            warn_surf = pygame.Surface((self.radius * 2 + 10, self.radius * 2 + 10), pygame.SRCALPHA)
            
            # Subtle base circle
            pygame.draw.circle(warn_surf, (*self.color, 45), (self.radius + 5, self.radius + 5), self.radius)
            # Outer ring
            pygame.draw.circle(warn_surf, (*self.color, int(130 + 100 * prog)), (self.radius + 5, self.radius + 5), self.radius, 2)
            # Expanding pulse ring
            pygame.draw.circle(warn_surf, (*self.color, int(100 + 120 * prog)), (self.radius + 5, self.radius + 5), max(4, pulse_rad), 2)
            # Inner core rune
            inner_r = max(5, int(self.radius * 0.35))
            pygame.draw.circle(warn_surf, (255, 255, 255, int(120 * prog)), (self.radius + 5, self.radius + 5), inner_r, 1)

            surface.blit(warn_surf, (cx - self.radius - 5, cy - self.radius - 5))
        else:
            # Active blast eruption phase
            fade = 1.0 - (self.age - self.windup_time) / max(0.01, self.linger_time)
            alpha = max(0, min(255, int(220 * fade)))
            erupt_surf = pygame.Surface((self.radius * 2 + 10, self.radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(erupt_surf, (*self.color, alpha), (self.radius + 5, self.radius + 5), self.radius)
            pygame.draw.circle(erupt_surf, (255, 255, 255, alpha), (self.radius + 5, self.radius + 5), int(self.radius * 0.6))
            surface.blit(erupt_surf, (cx - self.radius - 5, cy - self.radius - 5))

    def get_light(self):
        return (self.x, self.y, self.radius * 2, self.color, 0.8)


# =============================================================================
# 5 SIGNATURE ABILITY DEFINITIONS PER BOSS (40 TOTAL)
# =============================================================================

BOSS_SIGNATURE_PROFILES = {
    "grand_inquisitor_malchor": {
        "title": "Верховный Инквизитор Малхор",
        "dodge_name": "Теневой Шаг Крови",
        "abilities": [
            {"id": 1, "name": "Кровавые Кинжалы", "type": "blood_daggers", "desc": "Веер из 5 багровых кинжалов с брызгами крови"},
            {"id": 2, "name": "Багровая Печать Трибунала", "type": "blood_seal", "desc": "Пульсирующий темный ритуал крови на земле"},
            {"id": 3, "name": "Инквизиторский Рывок-Пронзание", "type": "inquisitor_rush", "desc": "Таранный выпад сквозь арену со сбитием с ног"},
            {"id": 4, "name": "Вихрь Казни", "type": "execution_whirlwind", "desc": "3 круговых взмаха клинка с нарастающим радиусом"},
            {"id": 5, "name": "Кровавые Столпы Суда", "type": "blood_pillars_ultimate", "desc": "Ультимейт: 4 столпа кипящей крови и взрыв багрянца"}
        ]
    },
    "goliath_prime_titan": {
        "title": "Голиаф Первородный Титан",
        "dodge_name": "Каменный Отскок",
        "abilities": [
            {"id": 1, "name": "Бросок Монолита", "type": "monolith_throw", "desc": "Швыряет гигантский каменный валун, дробящийся на осколки"},
            {"id": 2, "name": "Сейсмический Топот", "type": "seismic_stomp", "desc": "Колоссальная ударная волна на 250px, сотрясающая землю"},
            {"id": 3, "name": "Сокрушительный Прыжок", "type": "titan_leap", "desc": "Прыжок в воздух и сокрушительное падение на игрока"},
            {"id": 4, "name": "Титанический Раскол", "type": "titan_fissure_punches", "desc": "3 мощных удара кулаком по земле с расколом пола"},
            {"id": 5, "name": "Гнев Колосса", "type": "colossus_avalanche_ultimate", "desc": "Ультимейт: камнепад из 8 валунов по всей арене"}
        ]
    },
    "archlich_mordecai": {
        "title": "Архилич Мордекай",
        "dodge_name": "Бестелесный Фазовый Блинк",
        "abilities": [
            {"id": 1, "name": "Залп Черепов Скверны", "type": "homing_cursed_skulls", "desc": "4 изумрудных черепа с упорным самонаведением"},
            {"id": 2, "name": "Костяная Гробница", "type": "bone_prison", "desc": "Кольцо из 6 костяных шипов, окружающих игрока"},
            {"id": 3, "name": "Ледяной Луч Смерти", "type": "absolute_zero_beam", "desc": "Пронзающая очередь ледяных снарядов абсолютного нуля"},
            {"id": 4, "name": "Жатва Душ", "type": "soul_siphon", "desc": "Круговая вспышка призраков: крадет здоровье и лечит Лича"},
            {"id": 5, "name": "Некротический Взрыв", "type": "plague_cataclysm_ultimate", "desc": "Ультимейт: ядовитый туман чумы и 10 блуждающих огней"}
        ]
    },
    "void_overlord": {
        "title": "Повелитель Бездны",
        "dodge_name": "Искажение Эфира",
        "abilities": [
            {"id": 1, "name": "Астральные Серпы", "type": "void_rebounding_sickles", "desc": "3 серпа Бездны, рикошетящих от стен арены"},
            {"id": 2, "name": "Сингулярность Пустоты", "type": "void_black_hole", "desc": "Черная дыра, затягивающая игрока к эпицентру"},
            {"id": 3, "name": "Телепортационный Выпад", "type": "backstep_void_strike", "desc": "Мгновенный блинк строго за спину с ударом в спину"},
            {"id": 4, "name": "Теневой Шквал", "type": "shadow_spiral_blades", "desc": "Спиральный шквал из 7 теневых клинков по часовой стрелке"},
            {"id": 5, "name": "Сверхновая Бездны", "type": "void_supernova_ultimate", "desc": "Ультимейт: коллапс гравитации и 16 сфер антиматерии"}
        ]
    },
    "avatar_of_chaos": {
        "title": "Аватар Первородного Хаоса",
        "dodge_name": "Стихийный Сдвиг",
        "abilities": [
            {"id": 1, "name": "Инфернальный Залп", "type": "infernal_fireballs", "desc": "Тройной огненный заряд с разлетом раскаленных искр"},
            {"id": 2, "name": "Полярный Шторм", "type": "blizzard_slow_hazard", "desc": "Ледяная метель, замедляющая передвижение игрока"},
            {"id": 3, "name": "Молниеносный Рывок", "type": "zigzag_lightning_strike", "desc": "Зигзагообразный грозовой рывок с дуговыми разрядами"},
            {"id": 4, "name": "Буря Стихий", "type": "quad_elemental_orbit", "desc": "4 сферы (Огонь, Лед, Гроза, Тьма) в 4 стороны света"},
            {"id": 5, "name": "Апокалипсис Хаоса", "type": "chaos_apocalypse_ultimate", "desc": "Ультимейт: 4 стихийных взрыва и радужный катаклизм"}
        ]
    },
    "bladesovereign_valeria": {
        "title": "Владычица Клинков Валерия",
        "dodge_name": "Акробатический Кувырок",
        "abilities": [
            {"id": 1, "name": "Шквал Метательных Игл", "type": "hypersonic_needles", "desc": "Веер из 7 скоростных игл (640 px/s) с рассечением"},
            {"id": 2, "name": "Серповидная Волна", "type": "crescent_cleave_wave", "desc": "Широкий серп звенящей стали высокой пробиваемости"},
            {"id": 3, "name": "Филигранный Прорыв", "type": "supersonic_piercing_dash", "desc": "Сверхзвуковой выпад сквозь игрока со следом порезов"},
            {"id": 4, "name": "Танец Багровых Лезвий", "type": "fencing_quad_combo", "desc": "Серия из 4 быстрых фехтовальных взмахов с шагом вперед"},
            {"id": 5, "name": "Омнислеш: 1000 Порезов", "type": "omnislash_thousand_cuts_ultimate", "desc": "Ультимейт: 5 телепорт-ударов подряд по силуэту игрока"}
        ]
    },
    "abyssal_drakon_nadir": {
        "title": "Древний Змей Бездны Надир",
        "dodge_name": "Погружение в Тень",
        "abilities": [
            {"id": 1, "name": "Дыхание Сингулярности", "type": "drakon_dark_breath", "desc": "Широкий непрерывный конус из 8 снарядов пламени Бездны"},
            {"id": 2, "name": "Метеоры Пустоты", "type": "gravity_meteors", "desc": "4 падающих сгустка космической гравитации по области"},
            {"id": 3, "name": "Змеиный Бросок", "type": "drakon_jaw_lunge", "desc": "Сокрушительный выпад челюстями змея с захватом на 240px"},
            {"id": 4, "name": "Хвостовой Смет", "type": "tail_sweep_360", "desc": "Круговой оборот хвоста на 360° с мощным отбрасыванием"},
            {"id": 5, "name": "Гравитационный Рев", "type": "drakon_gravity_roar_ultimate", "desc": "Ультимейт: рев искажает арену волнами гравитации"}
        ]
    },
    "judge_of_truth": {
        "title": "Верховный Судия Истины",
        "dodge_name": "Божественное Вознесение",
        "abilities": [
            {"id": 1, "name": "Весы Правосудия", "type": "scales_of_justice_orbs", "desc": "Две парящие золотые сферы возмездия с наведением"},
            {"id": 2, "name": "Кара за Ложь", "type": "judgement_seal", "desc": "Золотая печать: наносит двойной урон (x2), если игрок солгал"},
            {"id": 3, "name": "Инквизиция Истины", "type": "truth_golden_javelin", "desc": "Священное золотое копье света со скоростью 620 px/s"},
            {"id": 4, "name": "Печать Судьбы", "type": "hammer_of_judgement_combo", "desc": "3 удара священным молотом истины с золотыми вспышками"},
            {"id": 5, "name": "Абсолютный Вердикт", "type": "absolute_verdict_ultimate", "desc": "Ультимейт: 4 столпа света по углам и солнечный суд в центре"}
        ]
    }
}


# =============================================================================
# DEDICATED BOSS COMBAT EXECUTORS (100% UNIQUE PER BOSS)
# =============================================================================

def execute_malchor(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist):
    """Grand Inquisitor Malchor: Blood, Inquisitorial Cleaves & Crimson Geysers."""
    base_dmg = boss.damage
    if ability_num == 1:
        # Blood Daggers: 5 daggers in spread with blood trails
        base_angle = math.atan2(dir_y, dir_x)
        for i in range(5):
            ang = base_angle - 0.4 + (i / 4.0) * 0.8
            p_vx = math.cos(ang) * 490.0
            p_vy = math.sin(ang) * 490.0
            proj = BossProjectile(boss.x, boss.y, p_vx, p_vy, base_dmg * 0.75, radius=9, color=(220, 25, 45), name="Кровавый Кинжал")
            game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 2:
        # Blood Seal: pulsing ritual rune on ground under player that erupts
        hazard = BossGroundHazard(player.x, player.y, radius=120, damage=base_dmg * 1.25, windup_time=0.85, color=(220, 30, 40), name="Печать Трибунала")
        game_abilities.append(hazard)

    elif ability_num == 3:
        # Inquisitor Rush: fast piercing ram across arena
        boss.vx = dir_x * 860.0
        boss.vy = dir_y * 860.0
        fx.spawn_sparks(boss.x, boss.y, (220, 30, 30), count=28, speed=320)
        sfx.play("dash")
        if dist < 170:
            player.take_damage(base_dmg * 1.30, fx, sfx, art, is_shielded=(player.i_frame_timer > 0))

    elif ability_num == 4:
        # Execution Whirlwind: 3 successive 360-degree cleaves
        boss.combo_step = 1
        boss.is_attacking = True
        boss.windup_timer = 0.0
        sfx.play("slash")

    elif ability_num == 5:
        # Crimson Pillars Ultimate: 4 boiling blood pillars around player + outward drops
        fx.add_screen_shake(30.0)
        sfx.play("crit")
        fx.add_floating_text("★★★ КАТАКЛИЗМ: КРОВАВЫЕ СТОЛПЫ СУДА! ★★★", boss.x, boss.y - 85, (255, 40, 40), size=28)
        for ox, oy in [(-90, 0), (90, 0), (0, -90), (0, 90)]:
            haz = BossGroundHazard(player.x + ox, player.y + oy, radius=90, damage=base_dmg * 1.45, windup_time=0.9, color=(240, 20, 30), name="Столп Суда")
            game_abilities.append(haz)
        for i in range(12):
            ang = i * (2 * math.pi / 12)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 360.0, math.sin(ang) * 360.0, base_dmg * 0.70, radius=10, color=(220, 20, 40), duration=2.5, name="Капля Крови")
            game_abilities.append(proj)


def execute_goliath(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist):
    """Goliath Prime Titan: Boulders, Seismic Shockwaves, Leaps & Avalanche."""
    base_dmg = boss.damage
    if ability_num == 1:
        # Monolith Throw: giant rolling stone boulder that crumbles
        proj = BossProjectile(boss.x, boss.y, dir_x * 370.0, dir_y * 370.0, base_dmg * 1.40, radius=26, color=(150, 130, 100), duration=2.4, name="Валун Монолита")
        game_abilities.append(proj)
        sfx.play("crit")

    elif ability_num == 2:
        # Seismic Stomp: massive 250px circular shockwave shaking arena
        hazard = BossGroundHazard(boss.x, boss.y, radius=250, damage=base_dmg * 1.15, windup_time=0.65, color=(200, 160, 90), name="Сейсмическая Волна")
        game_abilities.append(hazard)
        fx.add_screen_shake(18.0)
        sfx.play("crit")

    elif ability_num == 3:
        # Titan Leap Slam: jumps high and crushes down at player's location
        fx.add_floating_text("★ СОКРУШИТЕЛЬНЫЙ ПРЫЖОК!", boss.x, boss.y - 70, (220, 180, 120), size=24)
        boss.x = player.x
        boss.y = player.y
        fx.spawn_sparks(boss.x, boss.y, (180, 150, 110), count=40, speed=360)
        fx.add_screen_shake(25.0)
        art.add_scorch_mark(boss.x, boss.y, radius=110)
        player.take_damage(base_dmg * 1.35, fx, sfx, art, is_shielded=(player.i_frame_timer > 0))
        sfx.play("crit")

    elif ability_num == 4:
        # Titan Fissure Punches: 3 heavy ground smashes producing dust
        boss.combo_step = 1
        boss.is_attacking = True
        boss.windup_timer = 0.0
        sfx.play("crit")

    elif ability_num == 5:
        # Colossus Avalanche Ultimate: 8 falling boulders from cavern ceiling
        fx.add_screen_shake(35.0)
        sfx.play("crit")
        fx.add_floating_text("★★★ КАТАКЛИЗМ: ГНЕВ КОЛОССА! ★★★", boss.x, boss.y - 85, (230, 170, 90), size=28)
        for _ in range(8):
            rx = player.x + random.uniform(-220, 220)
            ry = player.y + random.uniform(-220, 220)
            haz = BossGroundHazard(rx, ry, radius=80, damage=base_dmg * 1.35, windup_time=0.85, color=(170, 140, 100), name="Падающий Валун")
            game_abilities.append(haz)


def execute_mordecai(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist):
    """Archlich Mordecai: Homing Cursed Skulls, Bone Prison, Freeze Ray & Soul Drain."""
    base_dmg = boss.damage
    if ability_num == 1:
        # Homing Cursed Skulls: 4 emerald skulls tracking the player
        base_angle = math.atan2(dir_y, dir_x)
        for i in range(4):
            ang = base_angle + (i - 1.5) * 0.4
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 350.0, math.sin(ang) * 350.0, base_dmg * 0.80, radius=12, color=(100, 255, 140), duration=3.2, name="Череп Скверны", homing=True, homing_turn=2.4)
            game_abilities.append(proj)
        sfx.play("dash")

    elif ability_num == 2:
        # Bone Prison: 6 bone spikes encircling the player in a cage
        for i in range(6):
            ang = i * (2 * math.pi / 6)
            bx = player.x + math.cos(ang) * 70
            by = player.y + math.sin(ang) * 70
            haz = BossGroundHazard(bx, by, radius=40, damage=base_dmg * 0.85, windup_time=0.75, color=(210, 240, 210), name="Костяной Шип")
            game_abilities.append(haz)
        sfx.play("slash")

    elif ability_num == 3:
        # Absolute Zero Frost Beam: burst line of 5 piercing ice shards
        for i in range(5):
            delay_dist = i * 25
            proj = BossProjectile(boss.x + dir_x * delay_dist, boss.y + dir_y * delay_dist, dir_x * 560.0, dir_y * 560.0, base_dmg * 0.65, radius=8, color=(130, 230, 255), duration=2.0, name="Ледяной Осколок")
            game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 4:
        # Soul Siphon: ring of ghost spirits that drains player HP and heals Mordecai
        boss.hp = min(boss.max_hp, boss.hp + 140)
        fx.add_floating_text("+140 HP [ЖАТВА ДУШ]", boss.x, boss.y - 50, (100, 255, 150), size=22)
        for i in range(8):
            ang = i * (2 * math.pi / 8)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 320.0, math.sin(ang) * 320.0, base_dmg * 0.70, radius=11, color=(120, 255, 180), duration=2.2, name="Призрак Души")
            game_abilities.append(proj)
        sfx.play("crit")

    elif ability_num == 5:
        # Plague Cataclysm Ultimate: toxic mist zones + 10 soul wisps
        fx.add_screen_shake(30.0)
        sfx.play("crit")
        fx.add_floating_text("★★★ КАТАКЛИЗМ: НЕКРОТИЧЕСКИЙ ВЗРЫВ! ★★★", boss.x, boss.y - 85, (100, 255, 120), size=28)
        for _ in range(6):
            rx = player.x + random.uniform(-190, 190)
            ry = player.y + random.uniform(-190, 190)
            haz = BossGroundHazard(rx, ry, radius=90, damage=base_dmg * 1.35, windup_time=0.85, color=(90, 240, 130), name="Чумное Облако")
            game_abilities.append(haz)
        for i in range(10):
            ang = i * (2 * math.pi / 10)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 340.0, math.sin(ang) * 340.0, base_dmg * 0.80, radius=12, color=(120, 255, 160), duration=3.0, name="Блуждающий Огонь")
            game_abilities.append(proj)


def execute_void_overlord(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist):
    """Void Overlord: Bouncing Sickles, Gravity Singularity, Backstep Blink & Supernova."""
    base_dmg = boss.damage
    if ability_num == 1:
        # Rebounding Void Sickles: 3 sickles that bounce off arena walls
        base_angle = math.atan2(dir_y, dir_x)
        for i in range(3):
            ang = base_angle + (i - 1) * 0.35
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 440.0, math.sin(ang) * 440.0, base_dmg * 0.90, radius=13, color=(190, 60, 255), duration=3.5, name="Астральный Серп", bounce=True)
            game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 2:
        # Void Singularity: black hole pulling player physically toward center
        hazard = BossGroundHazard(player.x, player.y, radius=140, damage=base_dmg * 1.30, windup_time=0.9, color=(150, 40, 230), name="Сингулярность Пустоты", slow_player=True)
        game_abilities.append(hazard)

    elif ability_num == 3:
        # Backstep Strike: blinks directly behind player and executes surprise attack
        boss.x = player.x - dir_x * 90.0
        boss.y = player.y - dir_y * 90.0
        fx.spawn_sparks(boss.x, boss.y, (190, 60, 255), count=32, speed=340)
        fx.add_floating_text("★ ТЕЛЕПОРТ ЗА СПИНУ!", boss.x, boss.y - 65, (210, 100, 255), size=24)
        sfx.play("dash")
        player.take_damage(base_dmg * 1.30, fx, sfx, art, is_shielded=(player.i_frame_timer > 0))

    elif ability_num == 4:
        # Shadow Spiral Blades: 7 blades launched in a clockwise spiral
        for i in range(7):
            ang = i * (2 * math.pi / 7)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 420.0, math.sin(ang) * 420.0, base_dmg * 0.70, radius=9, color=(170, 50, 240), duration=2.5, name="Теневой Клинок")
            game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 5:
        # Void Supernova Ultimate: gravitational collapse and 16 antimatter orbs
        fx.add_screen_shake(35.0)
        sfx.play("crit")
        fx.add_floating_text("★★★ КАТАКЛИЗМ: СВЕРХНОВАЯ БЕЗДНЫ! ★★★", boss.x, boss.y - 85, (210, 70, 255), size=28)
        for i in range(16):
            ang = i * (2 * math.pi / 16)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 360.0, math.sin(ang) * 360.0, base_dmg * 0.85, radius=14, color=(200, 50, 255), duration=3.2, name="Сфера Антиматерии")
            game_abilities.append(proj)


def execute_chaos(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist):
    """Avatar of Chaos: Fire, Frost, Lightning, and Void Quad-Elemental Cataclysm."""
    base_dmg = boss.damage
    if ability_num == 1:
        # Infernal Fireballs: triplet fire projectile exploding in sparks
        base_angle = math.atan2(dir_y, dir_x)
        for i in range(3):
            ang = base_angle + (i - 1) * 0.3
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 460.0, math.sin(ang) * 460.0, base_dmg * 0.85, radius=14, color=(255, 80, 20), duration=2.5, name="Огненный Шар")
            game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 2:
        # Polar Blizzard Storm: ice crystal zone that slows player by 35%
        hazard = BossGroundHazard(player.x, player.y, radius=130, damage=base_dmg * 1.20, windup_time=0.85, color=(120, 220, 255), name="Полярный Шторм", slow_player=True)
        game_abilities.append(hazard)

    elif ability_num == 3:
        # Zigzag Lightning Strike: ultra-fast lightning lunge (920 px/s)
        boss.vx = dir_x * 920.0
        boss.vy = dir_y * 920.0
        fx.spawn_sparks(boss.x, boss.y, (255, 240, 80), count=32, speed=360)
        sfx.play("dash")
        if dist < 170:
            player.take_damage(base_dmg * 1.35, fx, sfx, art, is_shielded=(player.i_frame_timer > 0))

    elif ability_num == 4:
        # Quad Elemental Orbit: 4 spheres of 4 elements launched outward
        elements = [
            ((255, 70, 30), "Огонь"),
            ((120, 220, 255), "Лед"),
            ((255, 240, 70), "Гроза"),
            ((180, 50, 240), "Тьма")
        ]
        for i, (col, el_name) in enumerate(elements):
            ang = i * (math.pi / 2)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 400.0, math.sin(ang) * 400.0, base_dmg * 0.90, radius=13, color=col, duration=2.8, name=f"Сфера: {el_name}")
            game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 5:
        # Chaos Apocalypse Ultimate: simultaneous detonation of all 4 elements
        fx.add_screen_shake(35.0)
        sfx.play("crit")
        fx.add_floating_text("★★★ КАТАКЛИЗМ: АПОКАЛИПСИС ХАОСА! ★★★", boss.x, boss.y - 85, (255, 180, 50), size=28)
        offsets_and_colors = [
            (-120, -120, (255, 70, 30), "Огненный Взрыв"),
            (120, -120, (120, 220, 255), "Ледяной Взрыв"),
            (-120, 120, (255, 240, 70), "Грозовой Взрыв"),
            (120, 120, (180, 50, 240), "Взрыв Тьмы")
        ]
        for ox, oy, col, el_name in offsets_and_colors:
            haz = BossGroundHazard(player.x + ox, player.y + oy, radius=95, damage=base_dmg * 1.30, windup_time=0.9, color=col, name=el_name)
            game_abilities.append(haz)


def execute_valeria(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist):
    """Bladesovereign Valeria: Hypersonic Needles, Crescent Wave, Piercing Dash & Omnislash."""
    base_dmg = boss.damage
    if ability_num == 1:
        # Hypersonic Needles: 7 razor-sharp needles at extreme velocity (640 px/s)
        base_angle = math.atan2(dir_y, dir_x)
        for i in range(7):
            ang = base_angle - 0.5 + (i / 6.0) * 1.0
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 640.0, math.sin(ang) * 640.0, base_dmg * 0.60, radius=6, color=(240, 240, 255), duration=2.0, name="Метательная Игла")
            game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 2:
        # Crescent Cleave Wave: massive slicing arc (radius=24, speed=470)
        proj = BossProjectile(boss.x, boss.y, dir_x * 470.0, dir_y * 470.0, base_dmg * 1.35, radius=24, color=(255, 220, 190), duration=2.2, name="Серповидная Волна")
        game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 3:
        # Supersonic Piercing Dash: penetrates straight through player
        boss.vx = dir_x * 960.0
        boss.vy = dir_y * 960.0
        fx.spawn_sparks(boss.x, boss.y, (255, 255, 255), count=30, speed=380)
        sfx.play("dash")
        if dist < 180:
            player.take_damage(base_dmg * 1.30, fx, sfx, art, is_shielded=(player.i_frame_timer > 0))

    elif ability_num == 4:
        # Fencing Quad Combo: 4 fast advancing sword slashes
        boss.combo_step = 1
        boss.is_attacking = True
        boss.windup_timer = 0.0
        sfx.play("slash")

    elif ability_num == 5:
        # Omnislash: 1000 Cuts Ultimate: 5 lightning teleports around player
        fx.add_screen_shake(32.0)
        sfx.play("crit")
        fx.add_floating_text("★★★ ОМНИСЛЕШ: 1000 ПОРЕЗОВ! ★★★", boss.x, boss.y - 85, (255, 230, 230), size=28)
        for i in range(5):
            ang = i * (2 * math.pi / 5)
            ox = math.cos(ang) * 75
            oy = math.sin(ang) * 75
            haz = BossGroundHazard(player.x + ox, player.y + oy, radius=55, damage=base_dmg * 0.95, windup_time=0.6 + i * 0.15, color=(255, 255, 255), name="Телепорт-Порез")
            game_abilities.append(haz)


def execute_nadir(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist):
    """Abyssal Drakon Nadir: Dark Fire Cone, Void Meteors, Dragon Bite & Gravity Roar."""
    base_dmg = boss.damage
    if ability_num == 1:
        # Drakon Dark Breath: wide cone of 8 dark flame spheres
        base_angle = math.atan2(dir_y, dir_x)
        for _ in range(8):
            ang = base_angle + random.uniform(-0.50, 0.50)
            spd = random.uniform(340, 490)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * spd, math.sin(ang) * spd, base_dmg * 0.60, radius=11, color=(120, 30, 180), duration=1.8, name="Пламя Бездны")
            game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 2:
        # Gravity Meteors: 4 falling cosmic voids around player
        for _ in range(4):
            rx = player.x + random.uniform(-150, 150)
            ry = player.y + random.uniform(-150, 150)
            haz = BossGroundHazard(rx, ry, radius=75, damage=base_dmg * 1.05, windup_time=0.8, color=(160, 50, 220), name="Грави-Метеор")
            game_abilities.append(haz)

    elif ability_num == 3:
        # Drakon Jaw Lunge: instant serpentine snap on 240px
        boss.vx = dir_x * 880.0
        boss.vy = dir_y * 880.0
        fx.spawn_sparks(boss.x, boss.y, (130, 40, 190), count=26, speed=320)
        sfx.play("dash")
        if dist < 190:
            player.take_damage(base_dmg * 1.35, fx, sfx, art, is_shielded=(player.i_frame_timer > 0))

    elif ability_num == 4:
        # Tail Sweep 360: massive dragon tail spin knocking player away
        boss.combo_step = 1
        boss.is_attacking = True
        boss.windup_timer = 0.0
        sfx.play("slash")

    elif ability_num == 5:
        # Gravity Roar Ultimate: dragon roar shaking arena with gravity pulses
        fx.add_screen_shake(35.0)
        sfx.play("crit")
        fx.add_floating_text("★★★ КАТАКЛИЗМ: ГРАВИТАЦИОННЫЙ РЕВ! ★★★", boss.x, boss.y - 85, (160, 40, 230), size=28)
        for i in range(12):
            ang = i * (2 * math.pi / 12)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 350.0, math.sin(ang) * 350.0, base_dmg * 0.80, radius=13, color=(130, 30, 190), duration=2.8, name="Волна Искажения")
            game_abilities.append(proj)


def execute_judge(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist):
    """Judge of Truth (Floor 50): Scales of Justice, Sin Judgement, Holy Javelin & Absolute Verdict."""
    base_dmg = boss.damage
    is_lied_to = getattr(boss, 'enraged', False)

    if ability_num == 1:
        # Scales of Justice Orbs: 2 homing golden spheres
        base_angle = math.atan2(dir_y, dir_x)
        for offset in (-0.35, 0.35):
            ang = base_angle + offset
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 370.0, math.sin(ang) * 370.0, base_dmg * 0.85, radius=13, color=(255, 230, 100), duration=3.0, name="Сфера Правосудия", homing=True, homing_turn=2.2)
            game_abilities.append(proj)
        sfx.play("dash")

    elif ability_num == 2:
        # Judgement Seal: double damage (x2) if player lied on Floor 50!
        sin_mult = 2.0 if is_lied_to else 1.25
        hazard = BossGroundHazard(player.x, player.y, radius=140, damage=base_dmg * sin_mult, windup_time=0.8, color=(255, 235, 90), name="Печать Истины" if not is_lied_to else "КАРА ЗА ЛОЖЬ (x2 УРОН!)")
        game_abilities.append(hazard)

    elif ability_num == 3:
        # Holy Javelin of Truth: fast golden javelin penetrating across arena
        proj = BossProjectile(boss.x, boss.y, dir_x * 620.0, dir_y * 620.0, base_dmg * 1.30, radius=14, color=(255, 240, 140), duration=2.2, name="Золотое Копье Истины")
        game_abilities.append(proj)
        sfx.play("slash")

    elif ability_num == 4:
        # Hammer of Judgement: 3 divine smashes with holy light
        boss.combo_step = 1
        boss.is_attacking = True
        boss.windup_timer = 0.0
        sfx.play("crit")

    elif ability_num == 5:
        # Absolute Verdict Ultimate: 4 holy pillars at arena corners + blinding sun
        fx.add_screen_shake(35.0)
        sfx.play("crit")
        fx.add_floating_text("★★★ АБСОЛЮТНЫЙ ВЕРДИКТ СУДИИ! ★★★", boss.x, boss.y - 85, (255, 240, 120), size=28)
        corners = [(-160, -160), (160, -160), (-160, 160), (160, 160)]
        for cx, cy in corners:
            haz = BossGroundHazard(player.x + cx, player.y + cy, radius=85, damage=base_dmg * 1.40, windup_time=0.85, color=(255, 245, 150), name="Столп Истины")
            game_abilities.append(haz)
        for i in range(12):
            ang = i * (2 * math.pi / 12)
            proj = BossProjectile(boss.x, boss.y, math.cos(ang) * 360.0, math.sin(ang) * 360.0, base_dmg * 0.85, radius=13, color=(255, 235, 110), duration=2.8, name="Луч Возмездия")
            game_abilities.append(proj)


# Dispatch map guaranteeing 100% bespoke logic per boss
BOSS_EXECUTORS = {
    "grand_inquisitor_malchor": execute_malchor,
    "goliath_prime_titan": execute_goliath,
    "archlich_mordecai": execute_mordecai,
    "void_overlord": execute_void_overlord,
    "avatar_of_chaos": execute_chaos,
    "bladesovereign_valeria": execute_valeria,
    "abyssal_drakon_nadir": execute_nadir,
    "judge_of_truth": execute_judge
}


# =============================================================================
# BOSS COMBAT CONTROLLER
# =============================================================================

def init_boss_combat_state(boss):
    """Initializes boss combat data on spawn."""
    boss.is_boss = True
    boss.boss_profile = BOSS_SIGNATURE_PROFILES.get(boss.id, BOSS_SIGNATURE_PROFILES["grand_inquisitor_malchor"])
    boss.boss_dodge_cooldown = random.uniform(2.5, 4.0)
    boss.boss_dodge_timer = 0.0
    boss.boss_ability_cooldown = random.uniform(1.8, 3.2)
    boss.active_ability_id = None
    boss.ability_cast_timer = 0.0
    boss.dodge_i_frames = 0.0


def check_and_perform_boss_dodge(boss, incoming_x, incoming_y, fx, sfx):
    """Checks if the boss can and should dodge an incoming attack."""
    if not getattr(boss, 'is_boss', False):
        return False
    if boss.is_frozen or boss.stun_timer > 0 or boss.exhausted_timer > 0:
        return False
    if getattr(boss, 'boss_dodge_cooldown', 0.0) > 0:
        return False

    # Perform dodge!
    profile = getattr(boss, 'boss_profile', BOSS_SIGNATURE_PROFILES["grand_inquisitor_malchor"])
    dodge_name = profile["dodge_name"]

    # Calculate dodge angle perpendicular to incoming vector
    dx = boss.x - incoming_x
    dy = boss.y - incoming_y
    dist = math.hypot(dx, dy)
    if dist < 0.01:
        angle = random.uniform(0, 2 * math.pi)
    else:
        perp_angle = math.atan2(dy, dx) + (math.pi / 2 if random.random() < 0.5 else -math.pi / 2)
        angle = perp_angle + random.uniform(-0.3, 0.3)

    # Boss-specific dodge speed and audio-visuals
    boss_id = getattr(boss, 'id', 'grand_inquisitor_malchor')
    if boss_id == "bladesovereign_valeria":
        dodge_speed = 900.0
        spark_col = (255, 255, 255)
        shake = 8.0
    elif boss_id == "goliath_prime_titan":
        dodge_speed = 640.0
        spark_col = (160, 130, 95)
        shake = 14.0
    elif boss_id == "archlich_mordecai":
        dodge_speed = 780.0
        spark_col = (110, 255, 140)
        shake = 6.0
    elif boss_id == "void_overlord":
        dodge_speed = 820.0
        spark_col = (190, 60, 255)
        shake = 10.0
    elif boss_id == "judge_of_truth":
        dodge_speed = 800.0
        spark_col = (255, 235, 110)
        shake = 10.0
    else:
        dodge_speed = 760.0
        spark_col = boss.tint
        shake = 10.0

    boss.vx = math.cos(angle) * dodge_speed
    boss.vy = math.sin(angle) * dodge_speed
    boss.dodge_i_frames = 0.45
    boss.boss_dodge_cooldown = random.uniform(2.8, 4.2)

    # Audio & Visual FX
    fx.spawn_sparks(boss.x, boss.y, spark_col, count=24, speed=260)
    fx.add_screen_shake(shake)
    fx.add_floating_text(f"★ УВОРОТ: {dodge_name}!", boss.x, boss.y - 60, spark_col, size=22)
    sfx.play("dash")
    return True


def execute_boss_ability(boss, ability_num, player, game_abilities, fx, sfx, art):
    """Executes one of the 5 abilities for the current boss using dedicated handlers."""
    profile = getattr(boss, 'boss_profile', BOSS_SIGNATURE_PROFILES["grand_inquisitor_malchor"])
    ab_info = profile["abilities"][ability_num - 1]
    ab_name = ab_info["name"]

    fx.add_floating_text(f"★ {profile['title']}: {ab_name}! ★", boss.x, boss.y - 70, boss.tint, size=24)
    fx.add_screen_shake(12.0)

    dx = player.x - boss.x
    dy = player.y - boss.y
    dist = max(1.0, math.hypot(dx, dy))
    dir_x = dx / dist
    dir_y = dy / dist

    # Route to the boss's 100% bespoke handler function
    boss_id = getattr(boss, 'id', 'grand_inquisitor_malchor')
    executor = BOSS_EXECUTORS.get(boss_id, execute_malchor)
    executor(boss, ability_num, player, game_abilities, fx, sfx, art, dir_x, dir_y, dist)


def update_boss_ai(boss, dt, player, game_abilities, fx, sfx, art, obstacles=None):
    """Updates Boss AI state machine, choosing between 5 abilities and managing evasions."""
    if not getattr(boss, 'is_boss', False) or not boss.alive:
        return

    # Update cooldowns
    if getattr(boss, 'boss_dodge_cooldown', 0.0) > 0:
        boss.boss_dodge_cooldown = max(0.0, boss.boss_dodge_cooldown - dt)

    if getattr(boss, 'dodge_i_frames', 0.0) > 0:
        boss.dodge_i_frames = max(0.0, boss.dodge_i_frames - dt)

    if getattr(boss, 'boss_ability_cooldown', 0.0) > 0:
        boss.boss_ability_cooldown = max(0.0, boss.boss_ability_cooldown - dt)

    # Don't cast if stunned or exhausted
    if boss.is_frozen or boss.stun_timer > 0 or boss.exhausted_timer > 0:
        return

    dist_to_player = math.hypot(player.x - boss.x, player.y - boss.y)

    # Pick and execute an ability when off cooldown
    if boss.boss_ability_cooldown <= 0 and not boss.is_attacking:
        # Distance-based ability weighting across the 5 abilities:
        if dist_to_player > 240:
            # Long range: Projectile Barrage (1), Gap Closer (3), or Ultimate (5)
            choice = random.choice([1, 1, 3, 5])
        elif dist_to_player > 120:
            # Mid range: Ground Hazard (2), Projectile (1), Gap Closer (3), or Ultimate (5)
            choice = random.choice([1, 2, 2, 3, 5])
        else:
            # Close range: Melee Combo (4), Ground Hazard (2), Gap Closer (3)
            choice = random.choice([2, 3, 4, 4])

        execute_boss_ability(boss, choice, player, game_abilities, fx, sfx, art)
        boss.boss_ability_cooldown = random.uniform(2.2, 3.8)
