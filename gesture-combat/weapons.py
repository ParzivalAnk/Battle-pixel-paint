"""
weapons.py - Expanded Weapon Arsenal & Dropped Weapon Loot System for GLYPH-BLADE.
Implements 5 rarity tiers:
- Tier 1 (Lowest / Самое фиговое): RED / ORANGE GLOW (Красное или оранжевое свечение)
- Tier 2: AMBER / GOLD GLOW
- Tier 3: VIOLET / ARCANE GLOW
- Tier 4: CELESTIAL CYAN GLOW
- Tier 5 (Highest / Самое крутое): PURE RADIANT WHITE GLOW (Чисто белое ослепительное свечение)
"""

import math
import random
import pygame

# =============================================================================
# TIER DEFINITIONS & GLOW COLORS
# =============================================================================
TIER_INFO = {
    1: {
        "name": "Ранг I: Ржавое / Обычное",
        "short_name": "РАНГ I",
        "glow_color": (255, 75, 30),        # Red / Orange glow (самое фиговое!)
        "beam_color": (255, 90, 40),
        "light_radius": 100,
        "badge_border": (255, 80, 40)
    },
    2: {
        "name": "Ранг II: Закаленное",
        "short_name": "РАНГ II",
        "glow_color": (255, 195, 45),       # Amber / Gold
        "beam_color": (255, 210, 60),
        "light_radius": 140,
        "badge_border": (255, 205, 50)
    },
    3: {
        "name": "Ранг III: Арканное",
        "short_name": "РАНГ III",
        "glow_color": (210, 80, 255),       # Violet / Purple
        "beam_color": (220, 100, 255),
        "light_radius": 180,
        "badge_border": (215, 90, 255)
    },
    4: {
        "name": "Ранг IV: Астральное",
        "short_name": "РАНГ IV",
        "glow_color": (70, 235, 255),       # Celestial Cyan
        "beam_color": (90, 245, 255),
        "light_radius": 230,
        "badge_border": (80, 240, 255)
    },
    5: {
        "name": "Ранг V: Первородное / Божественное",
        "short_name": "РАНГ V",
        "glow_color": (255, 255, 255),      # PURE RADIANT WHITE GLOW (самое крутое!)
        "beam_color": (255, 255, 255),
        "light_radius": 340,
        "badge_border": (255, 255, 255)
    }
}


class Weapon:
    def __init__(
        self,
        key: str,
        name: str,
        tier: int,
        weight: float,
        damage_mult: float,
        speed_mult: float,
        recovery_mult: float,
        fumble_stun: float,
        combo_window: float,
        icon: str = "⚔",
        desc: str = "",
        perk_desc: str = "",
        lifesteal_bonus: float = 0.0,
        bonus_time: float = 0.0,
        freeze_bonus: float = 0.0
    ):
        self.key = key
        self.name = name
        self.tier = tier
        t_data = TIER_INFO[tier]
        self.tier_name = t_data["name"]
        self.short_tier = t_data["short_name"]
        self.glow_color = t_data["glow_color"]
        self.color = self.glow_color
        self.beam_color = t_data["beam_color"]
        self.light_radius = t_data["light_radius"]

        self.weight = weight                    # kg
        self.damage_mult = damage_mult          # multiplier
        self.speed_mult = speed_mult            # affects player move speed
        self.recovery_mult = recovery_mult      # affects attack delay
        self.fumble_stun = fumble_stun          # penalty in seconds on fumble
        self.combo_window = combo_window        # seconds to continue combo
        self.icon = icon
        self.desc = desc
        self.perk_desc = perk_desc
        self.lifesteal_bonus = lifesteal_bonus
        self.bonus_time = bonus_time
        self.freeze_bonus = freeze_bonus

    def __repr__(self):
        return f"<Weapon {self.name} (Tier {self.tier}) dmg={self.damage_mult}>"


# =============================================================================
# EXPANDED CATALOG OF 25 WEAPONS
# =============================================================================
WEAPONS_CATALOG = {
    # -------------------------------------------------------------------------
    # TIER 1 (Самое фиговое): КРАСНОЕ / ОРАНЖЕВОЕ СВЕЧЕНИЕ (Red / Orange Glow)
    # -------------------------------------------------------------------------
    "rusty_cleaver": Weapon(
        key="rusty_cleaver",
        name="«Ржавый Тесак Мясника»",
        tier=1,
        weight=6.5,
        damage_mult=0.65,
        speed_mult=0.90,
        recovery_mult=1.35,
        fumble_stun=0.55,
        combo_window=0.85,
        icon="🪓",
        desc="Зазубренный мясницкий топор. Металл изъеден ржавчиной и кровью жертв.",
        perk_desc="Тяжелый замах, низкий урон заклинаний. [Красное свечение]"
    ),
    "chipped_dagger": Weapon(
        key="chipped_dagger",
        name="«Сколотый Кинжал Разбойника»",
        tier=1,
        weight=1.5,
        damage_mult=0.70,
        speed_mult=1.15,
        recovery_mult=0.85,
        fumble_stun=0.25,
        combo_window=1.10,
        icon="🗡",
        desc="Короткий разбойничий клинок со сколотым лезвием. Быстрый, но слабый.",
        perk_desc="Легкий вес, пониженный урон. [Красное свечение]"
    ),
    "cracked_mace": Weapon(
        key="cracked_mace",
        name="«Треснувшая Булава Склепа»",
        tier=1,
        weight=11.0,
        damage_mult=0.85,
        speed_mult=0.80,
        recovery_mult=1.60,
        fumble_stun=0.70,
        combo_window=0.75,
        icon="🔨",
        desc="Древнее надгробное орудие из склепа. Рукоять шатается от старости.",
        perk_desc="Огромная инерция и долгая осечка. [Оранжевое свечение]"
    ),
    "dull_scythe": Weapon(
        key="dull_scythe",
        name="«Тупая Коса Могильщика»",
        tier=1,
        weight=7.8,
        damage_mult=0.75,
        speed_mult=0.92,
        recovery_mult=1.25,
        fumble_stun=0.45,
        combo_window=0.90,
        icon="⚔",
        desc="Затупившаяся коса погребального служителя. Размах широк, но лезвие затуплено.",
        perk_desc="Широкий размах, тупой срез. [Красное свечение]"
    ),
    "bent_shortsword": Weapon(
        key="bent_shortsword",
        name="«Погнутый Гладиус Новобранца»",
        tier=1,
        weight=3.5,
        damage_mult=0.72,
        speed_mult=1.00,
        recovery_mult=1.10,
        fumble_stun=0.38,
        combo_window=0.95,
        icon="🗡",
        desc="Погнутый в былых битвах тренировочный гладиус со ржавой гардой.",
        perk_desc="Нестабильный баланс, базовые характеристики. [Оранжевое свечение]"
    ),

    # -------------------------------------------------------------------------
    # TIER 2: ЯНТАРНО-ЗОЛОТОЕ СВЕЧЕНИЕ (Amber / Gold Glow)
    # -------------------------------------------------------------------------
    "iron_katana": Weapon(
        key="iron_katana",
        name="«Стальная Катана Ронина»",
        tier=2,
        weight=3.8,
        damage_mult=1.00,
        speed_mult=1.00,
        recovery_mult=1.00,
        fumble_stun=0.35,
        combo_window=1.00,
        icon="⚔",
        desc="Классический клинок бродячего ронина. Безупречный баланс и проверенная сталь.",
        perk_desc="Эталонный баланс скорости и урона. [Янтарное свечение]"
    ),
    "silver_rapier": Weapon(
        key="silver_rapier",
        name="«Серебряная Рапира Дуэлянта»",
        tier=2,
        weight=2.0,
        damage_mult=0.95,
        speed_mult=1.18,
        recovery_mult=0.70,
        fumble_stun=0.22,
        combo_window=1.25,
        icon="🗡",
        desc="Тонкое серебряное жало гильдии фехтовальщиков. Высочайшая скорость выпадов.",
        perk_desc="Скорость перемещения +18%, быстрое комбо. [Янтарное свечение]"
    ),
    "war_halberd": Weapon(
        key="war_halberd",
        name="«Алебарда Стража Бастиона»",
        tier=2,
        weight=9.5,
        damage_mult=1.30,
        speed_mult=0.88,
        recovery_mult=1.35,
        fumble_stun=0.55,
        combo_window=0.85,
        icon="🔱",
        desc="Тяжелое длинное древковое оружие дворцовой стражи. Пробивает строй врагов.",
        perk_desc="Повышенный урон заклинаний x1.30. [Золотое свечение]"
    ),
    "broadsword_vanguard": Weapon(
        key="broadsword_vanguard",
        name="«Палаш Авангарда»",
        tier=2,
        weight=5.5,
        damage_mult=1.15,
        speed_mult=0.96,
        recovery_mult=1.05,
        fumble_stun=0.30,
        combo_window=1.05,
        icon="⚔",
        desc="Надежный широкий клинок тяжелой пехоты. Устойчив к ударам колоссов.",
        perk_desc="Надежная прочность, мягкая осечка. [Золотистое свечение]"
    ),
    "spiked_morningstar": Weapon(
        key="spiked_morningstar",
        name="«Шипастый Моргенштерн»",
        tier=2,
        weight=8.0,
        damage_mult=1.25,
        speed_mult=0.90,
        recovery_mult=1.20,
        fumble_stun=0.48,
        combo_window=0.90,
        icon="🔨",
        desc="Шипастая стальная булава на цепи. Дробит каменных стражей и щиты.",
        perk_desc="Сокрушающий урон x1.25. [Янтарное свечение]"
    ),

    # -------------------------------------------------------------------------
    # TIER 3: ПУРПУРНО-ФИОЛЕТОВОЕ СВЕЧЕНИЕ (Violet / Arcane Glow)
    # -------------------------------------------------------------------------
    "void_edge": Weapon(
        key="void_edge",
        name="«Клинок Пустоты Бездны»",
        tier=3,
        weight=3.2,
        damage_mult=1.50,
        speed_mult=1.10,
        recovery_mult=0.85,
        fumble_stun=0.28,
        combo_window=1.20,
        icon="✦",
        desc="Закален в чернильной тьме между мирами. Разрезает пространство трещинами эфира.",
        perk_desc="Урон заклинаний x1.50, скорость бега +10%. [Фиолетовое свечение]"
    ),
    "inferno_glaive": Weapon(
        key="inferno_glaive",
        name="«Инфернальная Глефа»",
        tier=3,
        weight=6.8,
        damage_mult=1.65,
        speed_mult=0.94,
        recovery_mult=1.15,
        fumble_stun=0.40,
        combo_window=1.10,
        icon="🔥",
        desc="Лезвие охвачено негасимым пламенем глубин. Испепеляет плоть врагов.",
        perk_desc="Мощный урон огненных заклинаний x1.65. [Пурпурное свечение]"
    ),
    "frost_scythe": Weapon(
        key="frost_scythe",
        name="«Ледяная Коса Хлада»",
        tier=3,
        weight=5.0,
        damage_mult=1.55,
        speed_mult=1.02,
        recovery_mult=0.95,
        fumble_stun=0.32,
        combo_window=1.15,
        freeze_bonus=1.5,
        icon="❄",
        desc="Покрыта вечной синей изморозью. Увеличивает длительность стазиса врагов.",
        perk_desc="Урон x1.55, заморозка врагов длится на +1.5с дольше! [Аметистовое свечение]"
    ),
    "storm_saber": Weapon(
        key="storm_saber",
        name="«Штормовая Сабля Грозы»",
        tier=3,
        weight=2.5,
        damage_mult=1.45,
        speed_mult=1.22,
        recovery_mult=0.72,
        fumble_stun=0.20,
        combo_window=1.35,
        icon="⚡",
        desc="Искрит электрическими разрядами при каждом взмахе. Невероятно быстрая.",
        perk_desc="Скорость бега +22%, окно комбо расширено. [Фиолетовое свечение]"
    ),
    "soul_eater_blade": Weapon(
        key="soul_eater_blade",
        name="«Жнец Заблудших Душ»",
        tier=3,
        weight=4.2,
        damage_mult=1.60,
        speed_mult=1.00,
        recovery_mult=0.90,
        fumble_stun=0.35,
        combo_window=1.10,
        lifesteal_bonus=0.06,
        icon="🩸",
        desc="Голодный темный клинок, впитывающий жизненные силы убитых чудовищ.",
        perk_desc="Вампиризм: возвращает +6% HP от урона! [Ультрафиолетовое свечение]"
    ),

    # -------------------------------------------------------------------------
    # TIER 4: НЕБЕСНО-ГОЛУБОЕ СВЕЧЕНИЕ (Celestial Cyan Glow)
    # -------------------------------------------------------------------------
    "celestial_blade": Weapon(
        key="celestial_blade",
        name="«Астральный Рассекатель»",
        tier=4,
        weight=2.8,
        damage_mult=2.15,
        speed_mult=1.25,
        recovery_mult=0.65,
        fumble_stun=0.18,
        combo_window=1.45,
        icon="✦",
        desc="Выкован из осколков упавшей кометы. Сияет лазурным космическим светом.",
        perk_desc="Колоссальный урон x2.15, окно комбо +0.45с! [Астральный циан]"
    ),
    "chronos_stiletto": Weapon(
        key="chronos_stiletto",
        name="«Стилет Владыки Времени»",
        tier=4,
        weight=1.1,
        damage_mult=1.85,
        speed_mult=1.38,
        recovery_mult=0.50,
        fumble_stun=0.14,
        combo_window=1.60,
        bonus_time=20.0,
        icon="⌛",
        desc="Искривляет течение времени вокруг владельца. Добавляет секунды к таймеру.",
        perk_desc="Скорость +38%, +20 сек к таймеру этажа! [Небесно-голубое свечение]"
    ),
    "dragon_greatsword": Weapon(
        key="dragon_greatsword",
        name="«Двуручник Драконьей Крови»",
        tier=4,
        weight=12.0,
        damage_mult=2.45,
        speed_mult=0.86,
        recovery_mult=1.40,
        fumble_stun=0.50,
        combo_window=0.90,
        lifesteal_bonus=0.12,
        icon="🐉",
        desc="Гигантский клинок из чешуи древнего дракона Бездны. Непревзойденная мощь.",
        perk_desc="Разрушительный урон x2.45, вампиризм +12%! [Голубое свечение]"
    ),
    "phantom_twinblades": Weapon(
        key="phantom_twinblades",
        name="«Парные Клинки Фантома»",
        tier=4,
        weight=1.6,
        damage_mult=2.00,
        speed_mult=1.32,
        recovery_mult=0.58,
        fumble_stun=0.16,
        combo_window=1.50,
        icon="⚔",
        desc="Два призрачных серпа, оставляющие за собой световые фантомы разрезов.",
        perk_desc="Мгновенный откат атак, урон x2.00. [Яркий бирюзовый свет]"
    ),
    "abyssal_titan_cleaver": Weapon(
        key="abyssal_titan_cleaver",
        name="«Колосс Палача Бездны»",
        tier=4,
        weight=13.5,
        damage_mult=2.65,
        speed_mult=0.82,
        recovery_mult=1.55,
        fumble_stun=0.60,
        combo_window=0.85,
        icon="🪓",
        desc="Оружие титанических стражей преисподней. Раскалывает арену сейсмической волной.",
        perk_desc="Сверхтяжелый сокрушающий урон x2.65. [Циановое сияние]"
    ),

    # -------------------------------------------------------------------------
    # TIER 5 (Самое крутое): ЧИСТО БЕЛОЕ СВЕТЯЩЕЕСЯ (Pure Radiant White Glow)
    # -------------------------------------------------------------------------
    "divine_sun_blade": Weapon(
        key="divine_sun_blade",
        name="«Клинок Первородного Света (Экскалибур)»",
        tier=5,
        weight=3.0,
        damage_mult=3.00,
        speed_mult=1.30,
        recovery_mult=0.55,
        fumble_stun=0.12,
        combo_window=1.60,
        icon="☀",
        desc="Священный артефакт богов творения. Сияет ослепительным белым светом, рассеивая любую тьму!",
        perk_desc="УРОН x3.00! Ослепительное белое сияние освещает всю арену! [Белое свечение]"
    ),
    "godslayer_titan_edge": Weapon(
        key="godslayer_titan_edge",
        name="«Богоубийца: Абсолютный Раскол»",
        tier=5,
        weight=7.5,
        damage_mult=3.50,
        speed_mult=1.12,
        recovery_mult=0.80,
        fumble_stun=0.22,
        combo_window=1.35,
        icon="⚜",
        desc="Выкован для сокрушения бессмертных владык. Разрывает саму ткань реальности чистым светом.",
        perk_desc="МАКСИМАЛЬНЫЙ УРОН x3.50! Пробивает любые барьеры боссов! [Белое свечение]"
    ),
    "genesis_omni_wand": Weapon(
        key="genesis_omni_wand",
        name="«Скипетр Первородного Бытия»",
        tier=5,
        weight=1.4,
        damage_mult=2.85,
        speed_mult=1.40,
        recovery_mult=0.45,
        fumble_stun=0.08,
        combo_window=1.80,
        icon="❂",
        desc="Венец древней созидающей магии. Любой неточный глиф моментально стабилизируется эфиром.",
        perk_desc="Почти нулевая осечка (0.08s), окно комбо 1.80s, урон x2.85! [Белое свечение]"
    ),
    "seraph_judgement": Weapon(
        key="seraph_judgement",
        name="«Меч Серафима Судного Дня»",
        tier=5,
        weight=4.0,
        damage_mult=3.25,
        speed_mult=1.20,
        recovery_mult=0.60,
        fumble_stun=0.15,
        combo_window=1.50,
        lifesteal_bonus=0.15,
        icon="👑",
        desc="Карающий меч архангела правосудия. Окружает владельца божественным сияющим нимбом.",
        perk_desc="Урон x3.25, вампиризм +15%, божественный нимб света! [Белое свечение]"
    ),
    "infinity_light_katana": Weapon(
        key="infinity_light_katana",
        name="«Катана Бесконечного Белого Сияния»",
        tier=5,
        weight=2.2,
        damage_mult=3.15,
        speed_mult=1.35,
        recovery_mult=0.48,
        fumble_stun=0.10,
        combo_window=1.70,
        icon="★",
        desc="Оружие верховного мастера света. Оставляет за взмахами ослепительные белые разрезы в воздухе.",
        perk_desc="Молниеносный темп, урон x3.15, белые световые разрезы! [Белое свечение]"
    )
}

# Default starting weapons for slots 1, 2, 3
STARTER_WEAPONS = {
    1: WEAPONS_CATALOG["chipped_dagger"],       # Tier 1 (Light)
    2: WEAPONS_CATALOG["iron_katana"],          # Tier 2 (Balanced)
    3: WEAPONS_CATALOG["war_halberd"]           # Tier 2 (Heavy)
}

# Backward compatibility map
WEAPONS = {
    1: STARTER_WEAPONS[1],
    2: STARTER_WEAPONS[2],
    3: STARTER_WEAPONS[3]
}


# =============================================================================
# DROPPED WEAPON ENTITY & LOOT BEAM RENDERING
# =============================================================================
class DroppedWeapon:
    """
    Interactive dropped weapon on the arena floor.
    Features:
    - Vertical loot beam (White for Tier 5, Red/Orange for Tier 1, etc.)
    - Bobbing floating icon and pulsing aura
    - Dynamic light emission
    - Floating inspect/pickup card when player walks near
    """
    def __init__(self, weapon: Weapon, x: float, y: float):
        self.weapon = weapon
        self.x = float(x)
        self.y = float(y)
        self.anim_time = random.uniform(0.0, 6.28)
        self.alive = True
        self.pickup_radius = 65.0

    def update(self, dt: float):
        self.anim_time += dt

    def get_light(self):
        """Returns light parameters for dynamic illumination in the arena."""
        return (
            self.x,
            self.y,
            self.weapon.light_radius,
            self.weapon.glow_color,
            0.95 if self.weapon.tier >= 4 else 0.80
        )

    def draw(self, surface: pygame.Surface, off_x: float, off_y: float, anim_time: float, fonts: dict, is_player_near: bool = False, current_player_weapon: Weapon = None):
        wx = int(self.x + off_x)
        wy = int(self.y + off_y)

        # Skip drawing if off-screen
        sw, sh = surface.get_size()
        if wx < -100 or wx > sw + 100 or wy < -100 or wy > sh + 100:
            return

        tier = self.weapon.tier
        col = self.weapon.glow_color
        pulse = 0.5 + 0.5 * math.sin(anim_time * 4.5 + self.anim_time)
        bob_y = int(math.sin(anim_time * 3.5 + self.anim_time) * 5)

        # ---------------------------------------------------------------------
        # 1. GROUND CIRCLES & RADIAL AURA
        # ---------------------------------------------------------------------
        base_r = int(18 + 6 * pulse + tier * 3)
        # Outer faint ring
        pygame.draw.ellipse(surface, (col[0] // 3, col[1] // 3, col[2] // 3), (wx - base_r, wy - base_r // 2, base_r * 2, base_r), 1)
        # Inner glowing ring
        inner_r = int(12 + 4 * pulse)
        pygame.draw.ellipse(surface, col, (wx - inner_r, wy - inner_r // 2, inner_r * 2, inner_r), 2)

        # ---------------------------------------------------------------------
        # 2. VERTICAL LOOT BEAM (White for Tier 5, Red/Orange for Tier 1)
        # ---------------------------------------------------------------------
        beam_h = 75 + tier * 18
        beam_w = 6 + tier * 3
        beam_surf = pygame.Surface((beam_w * 4, beam_h), pygame.SRCALPHA)
        
        # Pillar alpha gradient
        for y_step in range(beam_h):
            prog = 1.0 - (y_step / beam_h)
            alpha = int((120 + 80 * pulse) * prog)
            if tier == 5:
                # Tier 5: Pure Brilliant White Core + Silver Edge
                b_color = (255, 255, 255, min(255, alpha + 40))
                pygame.draw.line(beam_surf, b_color, (beam_w * 2 - beam_w // 2, beam_h - y_step), (beam_w * 2 + beam_w // 2, beam_h - y_step), 2)
            else:
                b_color = (col[0], col[1], col[2], alpha)
                pygame.draw.line(beam_surf, b_color, (beam_w * 2 - beam_w // 2, beam_h - y_step), (beam_w * 2 + beam_w // 2, beam_h - y_step), 1)

        surface.blit(beam_surf, (wx - beam_w * 2, wy - beam_h))

        # ---------------------------------------------------------------------
        # 3. FLOATING WEAPON ORB & ICON
        # ---------------------------------------------------------------------
        obj_y = wy - 22 + bob_y
        
        # Halo glow
        halo_r = 14 + int(4 * pulse) + (6 if tier == 5 else 0)
        halo_surf = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
        h_alpha = 180 if tier == 5 else 120
        pygame.draw.circle(halo_surf, (col[0], col[1], col[2], h_alpha), (halo_r, halo_r), halo_r)
        surface.blit(halo_surf, (wx - halo_r, obj_y - halo_r))

        # Diamond / Weapon Core
        diamond_pts = [
            (wx, obj_y - 12),
            (wx + 10, obj_y),
            (wx, obj_y + 12),
            (wx - 10, obj_y)
        ]
        pygame.draw.polygon(surface, (20, 22, 34), diamond_pts)
        pygame.draw.polygon(surface, col, diamond_pts, 2)
        if tier == 5:
            pygame.draw.circle(surface, (255, 255, 255), (wx, obj_y), 4)

        # Weapon Icon Symbol
        if fonts and "sym_small" in fonts:
            ic_s = fonts["sym_small"].render(self.weapon.icon, True, col)
            surface.blit(ic_s, (wx - ic_s.get_width() // 2, obj_y - ic_s.get_height() // 2))

        # Little rising sparkles
        for sp_idx in range(3):
            sp_ang = anim_time * 2.0 + sp_idx * (math.pi * 2 / 3) + self.anim_time
            sp_rad = 12 + sp_idx * 4
            sp_x = wx + int(math.cos(sp_ang) * sp_rad)
            sp_y = obj_y + int(math.sin(sp_ang) * 6) - (sp_idx * 8)
            pygame.draw.circle(surface, col, (sp_x, sp_y), 2 if tier < 5 else 3)

        # ---------------------------------------------------------------------
        # 4. INTERACTIVE TOOLTIP CARD (When player is near)
        # ---------------------------------------------------------------------
        if is_player_near and fonts:
            card_w = 380
            card_h = 105
            cx = max(10, min(sw - card_w - 10, wx - card_w // 2))
            cy = wy - beam_h - card_h - 14
            if cy < 10:
                cy = wy + 25

            # Card background
            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            card_bg = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_bg.fill((10, 14, 22, 235))
            surface.blit(card_bg, (cx, cy))
            pygame.draw.rect(surface, col, card_rect, 2, border_radius=6)

            # Rarity & Key Header
            hdr_text = f"[E] ЭКИПИРОВАТЬ: {self.weapon.short_tier}"
            hdr_s = fonts["small"].render(hdr_text, True, col)
            surface.blit(hdr_s, (cx + 10, cy + 8))

            # Weapon Name
            name_s = fonts["med"].render(self.weapon.name, True, (255, 255, 255) if tier == 5 else col)
            surface.blit(name_s, (cx + 10, cy + 28))

            # Objective stats line (player must read the values!)
            stat_text = f"Урон: x{self.weapon.damage_mult:.2f}  |  Вес: {self.weapon.weight} кг"
            stat_s = fonts["small"].render(stat_text, True, (215, 225, 240))
            surface.blit(stat_s, (cx + 10, cy + 54))

            # Lore / Perk / Desc
            perk_s = fonts["small"].render(self.weapon.perk_desc, True, (255, 225, 120) if tier >= 4 else (180, 190, 210))
            surface.blit(perk_s, (cx + 10, cy + 76))


# =============================================================================
# WEAPON LOOT ROLL GENERATOR
# =============================================================================
def roll_enemy_weapon_drop(enemy, floor_idx: int = 0) -> Weapon:
    """
    Rolls a weapon drop from a defeated enemy.
    Returns a Weapon instance if drop succeeds, else None.
    - Regular enemies: ~22% drop chance
    - Elites / Colossi: ~55% drop chance
    - Bosses: 100% GUARANTEED drop (and rolls Tier 3-5!)
    - Floor 50 Boss: 100% Tier 5 (Divine White)!
    """
    scale = getattr(enemy, 'scale', 1.0)
    e_name = getattr(enemy, 'name', '')
    e_id = getattr(enemy, 'id', '')
    is_boss = (scale > 1.35 or "БОСС" in e_name or "Титан" in e_name)
    is_elite = (scale > 1.2 and not is_boss)

    # Drop probability check
    if is_boss:
        drop_chance = 1.0
    elif is_elite:
        drop_chance = 0.55
    else:
        drop_chance = 0.22

    if random.random() > drop_chance:
        return None

    # Determine Tier distribution
    if is_boss:
        if e_id == "judge_of_truth" or floor_idx >= 4:
            # High floor boss / Level 50 Judge -> 60% Tier 5 (White), 40% Tier 4 (Cyan)
            rolled_tier = random.choices([4, 5], weights=[40, 60])[0]
        else:
            # Regular boss -> Tier 3 (30%), Tier 4 (45%), Tier 5 (25%)
            rolled_tier = random.choices([3, 4, 5], weights=[30, 45, 25])[0]
    elif is_elite:
        # Elite monster
        rolled_tier = random.choices([2, 3, 4, 5], weights=[35, 40, 20, 5])[0]
    else:
        # Regular monster based on floor depth
        if floor_idx <= 1:
            # Early floors: Mostly Tier 1 (Red/Orange) & Tier 2
            rolled_tier = random.choices([1, 2, 3], weights=[55, 35, 10])[0]
        elif floor_idx <= 3:
            # Mid floors
            rolled_tier = random.choices([1, 2, 3, 4], weights=[28, 42, 22, 8])[0]
        else:
            # Deep floors
            rolled_tier = random.choices([1, 2, 3, 4, 5], weights=[15, 28, 32, 18, 7])[0]

    # Select random weapon from chosen tier
    tier_weapons = [w for w in WEAPONS_CATALOG.values() if w.tier == rolled_tier]
    if not tier_weapons:
        tier_weapons = list(WEAPONS_CATALOG.values())

    return random.choice(tier_weapons)
