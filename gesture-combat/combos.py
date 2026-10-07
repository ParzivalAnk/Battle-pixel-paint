"""
Combos and Elemental Synthesis Engine for GLYPH-BLADE.
Implements the 17-Element/Setting System and 204 Ultra-Combo Matrix (17*3 + 17*4 + 17*5).
Supports drawing multi-glyph combinations (min 3 signs, up to 5) all at once.
"""

import math
import random
import pygame

# =============================================================================
# 17 НАСТРОЕК И СТИХИЙ (17 SETTINGS / ELEMENTS)
# 3 типа действия + 9 базовых стихий + 5 засекреченных стихий = 17
# =============================================================================
ELEMENTS = {
    # 3 Типа Действия / Зоны
    "AOE": {
        "id": "AOE",
        "name": "По Области (AoE)",
        "glyph": "SLASH_H",
        "symbol": "—",
        "desc": "Мгновенная детонация колоссального радиуса на всю арену.",
        "color": (255, 210, 80),
        "is_secret": False,
        "floor_unlock": 0
    },
    "ZONE": {
        "id": "ZONE",
        "name": "По Зоне Действия (Аура)",
        "glyph": "CIRCLE",
        "symbol": "O",
        "desc": "Затяжной пульсирующий шторм на земле, непрерывно калечащий врагов.",
        "color": (100, 240, 210),
        "is_secret": False,
        "floor_unlock": 0
    },
    "HP": {
        "id": "HP",
        "name": "По HP (Жатва)",
        "glyph": "THRUST",
        "symbol": ">",
        "desc": "Вампирическое исцеление игрока и казнь врагов с низким здоровьем.",
        "color": (255, 60, 90),
        "is_secret": False,
        "floor_unlock": 0
    },

    # 9 Базовых Стихий
    "FIRE": {
        "id": "FIRE",
        "name": "Инферно",
        "glyph": "UPPERCUT",
        "symbol": "^",
        "desc": "Яростное пламя, поджигающее плоть и детонирующее горение.",
        "color": (255, 120, 30),
        "is_secret": False,
        "floor_unlock": 0
    },
    "ICE": {
        "id": "ICE",
        "name": "Крио",
        "glyph": "PARRY",
        "symbol": "V",
        "desc": "Абсолютный мороз, сковывающий монстров в ледяной стазис.",
        "color": (140, 230, 255),
        "is_secret": False,
        "floor_unlock": 0
    },
    "LIGHTNING": {
        "id": "LIGHTNING",
        "name": "Гроза",
        "glyph": "ZIGZAG",
        "symbol": "Z",
        "desc": "Электрические дуги, парализующие током всю группу противников.",
        "color": (255, 255, 100),
        "is_secret": False,
        "floor_unlock": 0
    },
    "EARTH": {
        "id": "EARTH",
        "name": "Титан",
        "glyph": "SLASH_V",
        "symbol": "|",
        "desc": "Кинетическое сокрушение астероидами и раскол земной тверди.",
        "color": (240, 140, 50),
        "is_secret": False,
        "floor_unlock": 0
    },
    "CHRONO": {
        "id": "CHRONO",
        "name": "Бастион",
        "glyph": "SHIELD_BLOCK",
        "symbol": "🛡",
        "desc": "Купольная защита и 5-кратное замедление времени вокруг игрока.",
        "color": (255, 220, 80),
        "is_secret": False,
        "floor_unlock": 0
    },
    "STAR": {
        "id": "STAR",
        "name": "Звезда",
        "glyph": "STAR_PENTAGRAM",
        "symbol": "★",
        "desc": "Пятиконечная печать апокалипсиса, стирающая вражеские ряды.",
        "color": (255, 50, 50),
        "is_secret": False,
        "floor_unlock": 0
    },
    "BLADE": {
        "id": "BLADE",
        "name": "Разруб",
        "glyph": "CROSS",
        "symbol": "X",
        "desc": "Бронебойное рассечение плоти перекрестными световыми лезвиями.",
        "color": (255, 60, 140),
        "is_secret": False,
        "floor_unlock": 0
    },
    "PRISM": {
        "id": "PRISM",
        "name": "Призма",
        "glyph": "TRIANGLE",
        "symbol": "△",
        "desc": "Треугольный щит света, отражающий снаряды боссов.",
        "color": (100, 255, 200),
        "is_secret": False,
        "floor_unlock": 0
    },
    "OMNI": {
        "id": "OMNI",
        "name": "Петля",
        "glyph": "INFINITY",
        "symbol": "∞",
        "desc": "Шквал из десятка фантомных клинковых срезов в радиусе вокруг цели.",
        "color": (220, 120, 255),
        "is_secret": False,
        "floor_unlock": 0
    },

    # 5 Засекреченных Стихий (Secret Elements, открывающихся за этажи 1-5)
    "SUPERNOVA": {
        "id": "SUPERNOVA",
        "name": "Сверхновая",
        "glyph": "CROSS",
        "symbol": "✦",
        "desc": "Астральный взрыв перерожденной звезды, ослепляющий всю арену.",
        "color": (255, 130, 230),
        "is_secret": True,
        "floor_unlock": 1
    },
    "ABSOLUTE_ZERO": {
        "id": "ABSOLUTE_ZERO",
        "name": "Абсолютный Ноль",
        "glyph": "PARRY",
        "symbol": "❄",
        "desc": "Температура -273.15°C, навсегда замораживающая даже пламя.",
        "color": (80, 255, 255),
        "is_secret": True,
        "floor_unlock": 2
    },
    "CHRONO_SINGULARITY": {
        "id": "CHRONO_SINGULARITY",
        "name": "Сингулярность",
        "glyph": "HOURGLASS_SWAP",
        "symbol": "⌛",
        "desc": "Разрыв времени, заставляющий врагов получать урон из будущего.",
        "color": (210, 100, 255),
        "is_secret": True,
        "floor_unlock": 3
    },
    "ANTIMATTER": {
        "id": "ANTIMATTER",
        "name": "Антиматерия",
        "glyph": "INFINITY",
        "symbol": "⚛",
        "desc": "Аннигиляция молекул противников при соприкосновении с вакуумом.",
        "color": (255, 50, 180),
        "is_secret": True,
        "floor_unlock": 4
    },
    "PRIMORDIAL_CHAOS": {
        "id": "PRIMORDIAL_CHAOS",
        "name": "Первородный Хаос",
        "glyph": "CUSTOM_GLYPH",
        "symbol": "❂",
        "desc": "Древнейшая энергия сотворения мира, обращающая боссов в прах.",
        "color": (255, 240, 90),
        "is_secret": True,
        "floor_unlock": 5
    }
}

ELEMENT_LIST = list(ELEMENTS.keys()) # 17 элементов
TOTAL_SETTINGS_COUNT = len(ELEMENT_LIST) # ровно 17!

# Map glyph name from recognizer to element key
GLYPH_TO_ELEMENT = {
    "SLASH_H": "AOE",
    "CIRCLE": "ZONE",
    "THRUST": "HP",
    "UPPERCUT": "FIRE",
    "PARRY": "ICE",
    "ZIGZAG": "LIGHTNING",
    "SLASH_V": "EARTH",
    "SHIELD_BLOCK": "CHRONO",
    "STAR_PENTAGRAM": "STAR",
    "CROSS": "BLADE",
    "TRIANGLE": "PRISM",
    "INFINITY": "OMNI",
    "HOURGLASS_SWAP": "CHRONO_SINGULARITY",
    "CUSTOM_GLYPH": "PRIMORDIAL_CHAOS"
}


# =============================================================================
# УЛЬТРА-СПОСОБНОСТИ ДЛЯ СИНТЕЗИРОВАННЫХ КОМБО
# =============================================================================
class UltraComboAbility:
    def __init__(self, name, combo_type, damage_mult, duration, elements, color):
        self.name = name
        self.combo_type = combo_type
        self.damage_mult = damage_mult
        self.duration = duration
        self.age = 0.0
        self.alive = True
        self.elements = elements
        self.color = color
        self.triggered = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        self.age += dt

    def draw(self, surface, offset_x=0, offset_y=0):
        pass

    def get_light(self):
        return None


class UltraFreezeCataclysm(UltraComboAbility):
    """
    [★] + [^] + [V]: УЛЬТРА-ЗАМОРОЗКА (ПОЛЯРНЫЙ КАТАКЛИЗМ)
    Мгновенно замораживает ВСЕХ врагов и боссов на всей арене,
    затем раскалывает их метеоритным крио-взрывом!
    """
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__("Ультра-Заморозка: Полярный Катаклизм", "ULTRA_FREEZE", damage_mult * 2.8, 2.5, ["STAR", "FIRE", "ICE"], (140, 240, 255))
        self.x = float(target_x)
        self.y = float(target_y)
        self.shattered = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        # Step 1: Immediate flash freeze of entire arena!
        if not self.triggered:
            self.triggered = True
            fx.add_screen_shake(25.0)
            sfx.play("parry")
            for en in enemies:
                if en.alive:
                    en.is_frozen = True
                    en.stun_timer = max(en.stun_timer, 4.0)
                    fx.spawn_sparks(en.x, en.y, (140, 230, 255), count=18, speed=160)
                    fx.add_floating_text("❄ АБСОЛЮТНАЯ ЗАМОРОЗКА!", en.x, en.y - 45, (140, 230, 255), size=24)

        # Step 2: Apocalyptic Shatter after 0.8s
        if self.age >= 0.8 and not self.shattered:
            self.shattered = True
            fx.add_screen_shake(32.0)
            art.add_scorch_mark(self.x, self.y, radius=110)
            sfx.play("crit")

            for en in enemies:
                if en.alive:
                    dist = math.hypot(self.x - en.x, self.y - en.y)
                    # All frozen enemies shatter!
                    dmg = (180.0 if dist < 320 else 120.0) * self.damage_mult
                    en.is_frozen = False
                    en.take_hit(dmg, random.uniform(-400, 400), random.uniform(-400, 400), 2.0, True, fx, sfx, spell_tag="УЛЬТРА-ЗАМОРОЗКА", player=player)
                    fx.spawn_sparks(en.x, en.y, (180, 245, 255), count=30, speed=360)
                    fx.add_floating_text(f"❄ РАСКОЛ КАТАКЛИЗМА! -{int(dmg)}", en.x, en.y - 50, (255, 255, 255), size=30)

        if self.age >= self.duration:
            self.alive = False

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        prog = min(1.0, self.age / 0.8)
        rad = int(140 + 90 * prog)

        # Blizzard vortex ring
        ring_surf = pygame.Surface((rad * 2 + 10, rad * 2 + 10), pygame.SRCALPHA)
        alpha = int(220 * (1.0 - (self.age / self.duration)))
        pygame.draw.circle(ring_surf, (140, 240, 255, alpha), (rad + 5, rad + 5), rad, 6)
        pygame.draw.circle(ring_surf, (255, 255, 255, alpha), (rad + 5, rad + 5), int(rad * 0.7), 3)

        # Ice crystalline spikes
        for i in range(8):
            ang = self.age * 3.0 + i * (math.pi / 4)
            px = rad + 5 + int(rad * math.cos(ang))
            py = rad + 5 + int(rad * math.sin(ang))
            pygame.draw.circle(ring_surf, (220, 250, 255, alpha), (px, py), 6)

        surface.blit(ring_surf, (cx - rad - 5, cy - rad - 5))

    def get_light(self):
        return (self.x, self.y, 350, (140, 240, 255), 1.0)


class GenericUltraComboSpell(UltraComboAbility):
    """Procedurally synthesizes high-impact effects for all other 3, 4, 5-glyph combinations."""
    def __init__(self, target_x, target_y, name, damage_mult, elements, color):
        super().__init__(name, "ULTRA_GENERIC", damage_mult, 1.8, elements, color)
        self.x = float(target_x)
        self.y = float(target_y)
        self.has_detonated = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if self.age >= 0.35 and not self.has_detonated:
            self.has_detonated = True
            fx.add_screen_shake(26.0 + len(self.elements) * 3.0)
            fx.spawn_sparks(self.x, self.y, self.color, count=50 + len(self.elements) * 15, speed=420)
            art.add_scorch_mark(self.x, self.y, radius=70 + len(self.elements) * 10)
            sfx.play("crit")

            # Check if HP / Vampiric is included
            has_hp = "HP" in self.elements or "BLOOD" in self.elements
            if has_hp:
                heal = int(35 * self.damage_mult)
                player.hp = min(player.max_hp, player.hp + heal)
                fx.add_floating_text(f"+{heal} HP (ВАМПИРИЗМ СИНТЕЗА)!", player.x, player.y - 45, (80, 255, 140), size=26)

            # Hit enemies
            rad = 240.0 + len(self.elements) * 35.0
            base_dmg = 110.0 + len(self.elements) * 35.0
            stag = self.name.split(':')[0].strip()
            for en in enemies:
                if en.alive:
                    dist = math.hypot(en.x - self.x, en.y - self.y)
                    if dist < rad:
                        dmg = base_dmg * self.damage_mult
                        en.take_hit(dmg, (en.x - self.x) * 3.5, (en.y - self.y) * 3.5, 1.8, True, fx, sfx, spell_tag=stag, player=player)
                        fx.add_floating_text(f"★ {stag}! -{int(dmg)}", en.x, en.y - 45, self.color, size=26)

        if self.age >= self.duration:
            self.alive = False

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        prog = min(1.0, self.age / 0.35)
        rad = int((120 + len(self.elements) * 25) * prog)
        alpha = int(240 * (1.0 - (self.age / self.duration)))

        ring = pygame.Surface((rad * 2 + 10, rad * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*self.color, alpha), (rad + 5, rad + 5), rad, 5)
        pygame.draw.circle(ring, (255, 255, 255, alpha), (rad + 5, rad + 5), int(rad * 0.6), 3)
        surface.blit(ring, (cx - rad - 5, cy - rad - 5))

    def get_light(self):
        return (self.x, self.y, 300, self.color, 0.95)


# =============================================================================
# COMBO SYNTHESIS RECIPE ENGINE (17*3 + 17*4 + 17*5 = 204 УНИКАЛЬНЫХ КОМБО)
# =============================================================================
class ComboMatrix:
    """Manages the full library of 204 combos, checks unlocks, and handles synthesis."""

    def __init__(self):
        self.unlocked_secret_elements = set()
        self.synthesized_recipes = set()

    def update_floor_unlocks(self, floor_idx):
        """Unlocks secret elements based on dungeon progress."""
        for e_id, e_info in ELEMENTS.items():
            if e_info["is_secret"]:
                if floor_idx >= e_info["floor_unlock"]:
                    self.unlocked_secret_elements.add(e_id)

    def is_element_unlocked(self, elem_id):
        elem = ELEMENTS.get(elem_id)
        if not elem:
            return False
        if not elem["is_secret"]:
            return True
        return elem_id in self.unlocked_secret_elements

    def resolve_combo(self, glyph_keys):
        """
        Takes a list of 3, 4, or 5 glyph keys or element IDs.
        Returns (combo_name, ability_class_or_callable, damage_multiplier, color, desc).
        """
        if len(glyph_keys) < 3:
            return None

        # Map glyphs to elements
        elements = []
        for k in glyph_keys:
            if k in ELEMENTS:
                elements.append(k)
            elif k in GLYPH_TO_ELEMENT:
                elements.append(GLYPH_TO_ELEMENT[k])
            else:
                elements.append("AOE")

        n = len(elements)
        elem_set = set(elements)

        # 1. SPECIAL SIGNATURE: [★] + [^] + [V] => УЛЬТРА-ЗАМОРОЗКА (ПОЛЯРНЫЙ КАТАКЛИЗМ)
        if ("STAR" in elem_set or "STAR_PENTAGRAM" in glyph_keys) and \
           ("FIRE" in elem_set or "UPPERCUT" in glyph_keys) and \
           ("ICE" in elem_set or "PARRY" in glyph_keys):
            return {
                "name": "❄ Ультра-Заморозка: Полярный Катаклизм",
                "tier": f"{n}-Glyph Ultra",
                "mult": 3.4 + (n - 3) * 0.7,
                "color": (140, 240, 255),
                "desc": "Мгновенная абсолютная заморозка всей арены с последующим сокрушительным расколом!",
                "creator": lambda tx, ty, mult: UltraFreezeCataclysm(tx, ty, mult)
            }

        # 2. Procedural Deterministic Synthesis for the 204 Permutations!
        # Primary element determines title prefix
        primary_elem = ELEMENTS.get(elements[0], ELEMENTS["STAR"])
        secondary_elem = ELEMENTS.get(elements[1], ELEMENTS["FIRE"])
        modifier_elem = ELEMENTS.get(elements[2], ELEMENTS["ICE"])

        prefixes = {
            "AOE": "Армагеддон", "ZONE": "Вихрь", "HP": "Кровавая Жатва",
            "FIRE": "Инфернальный", "ICE": "Ледяной", "LIGHTNING": "Громовой",
            "EARTH": "Титанический", "CHRONO": "Хроно", "STAR": "Катаклизм",
            "BLADE": "Рассекающий", "PRISM": "Призматический", "OMNI": "Бесконечный",
            "SUPERNOVA": "Сверхновый", "ABSOLUTE_ZERO": "Абсолютный", "CHRONO_SINGULARITY": "Сингулярный",
            "ANTIMATTER": "Антиматериальный", "PRIMORDIAL_CHAOS": "Первородный"
        }
        suffixes = {
            "AOE": "Разлом", "ZONE": "Шторм", "HP": "Коллапс",
            "FIRE": "Огонь", "ICE": "Стазис", "LIGHTNING": "Разряд",
            "EARTH": "Удар", "CHRONO": "Барьер", "STAR": "Апокалипсис",
            "BLADE": "Разруб", "PRISM": "Купол", "OMNI": "Омнислеш",
            "SUPERNOVA": "Вспышка", "ABSOLUTE_ZERO": "Ноль", "CHRONO_SINGULARITY": "Разрыв",
            "ANTIMATTER": "Аннигилятор", "PRIMORDIAL_CHAOS": "Хаос"
        }

        p1 = prefixes.get(elements[0], "Звездный")
        p2 = prefixes.get(elements[1], "Эфирный")
        s3 = suffixes.get(elements[2], "Взрыв")

        combo_name = f"★ {p1} {p2} {s3} [Ультра x{n}]"
        damage_mult = 2.4 + (n - 3) * 0.85
        color = primary_elem["color"]
        desc = f"Синтез из {n} знаков: {primary_elem['name']} + {secondary_elem['name']} + {modifier_elem['name']}."

        return {
            "name": combo_name,
            "tier": f"{n}-Glyph Ultra",
            "mult": damage_mult,
            "color": color,
            "desc": desc,
            "creator": lambda tx, ty, mult: GenericUltraComboSpell(tx, ty, combo_name, mult, elements, color)
        }


# Singleton instance
COMBO_MATRIX = ComboMatrix()
