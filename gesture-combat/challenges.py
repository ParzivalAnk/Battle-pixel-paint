"""
challenges.py - Challenge Modifiers & Hardcore Mutators System for GLYPH-BLADE
Implements modular challenge handicaps (e.g. ONLY DEBUFFS / ZERO BUFFS,
instant adaptation, brutal timer drain, glass cannon, and pitch darkness).
"""

import math
import pygame

class ChallengeModifier:
    def __init__(self, key, name, icon, color, short_tag, desc, penalty_desc, hotkey):
        self.key = key
        self.name = name
        self.icon = icon
        self.color = color
        self.short_tag = short_tag
        self.desc = desc
        self.penalty_desc = penalty_desc
        self.hotkey = hotkey

# Catalog of 7 Hardcore Challenge Modifiers
CHALLENGES = {
    "ONLY_CURSES": ChallengeModifier(
        key="ONLY_CURSES",
        name="Дары Скверны (Только Дебаффы)",
        icon="☠",
        color=(235, 75, 255),
        short_tag="ТОЛЬКО ДЕБАФФЫ",
        desc="В порталах НОЛЬ БАФФОВ: предлагаются только проклятые дары!",
        penalty_desc="100% предложений портала — чистые дебаффы без благословений.",
        hotkey="[1]"
    ),
    "HYPER_ADAPTATION": ChallengeModifier(
        key="HYPER_ADAPTATION",
        name="Абсолютная Адаптация (Анти-Спам)",
        icon="🛡",
        color=(100, 225, 255),
        short_tag="МГНОВ. ИММУНИТЕТ",
        desc="Враги включают 100% иммунитет ко 2-му удару стихии (боссы — с 1-го)!",
        penalty_desc="Спам-порог монстров = 2, боссов = 1. Длительность щита +50%.",
        hotkey="[2]"
    ),
    "DOOM_TIMER": ChallengeModifier(
        key="DOOM_TIMER",
        name="Песок Сквозь Пальцы (Таймер-Рок)",
        icon="⌛",
        color=(255, 140, 50),
        short_tag="ТАЙМЕР -6S ЗА УДАР",
        desc="Базовый таймер 75 сек. Пропущенный удар отнимает -6.0s времени этажа!",
        penalty_desc="Стартовый таймер урезан. Каждый пропущенный удар срезает 6 сек.",
        hotkey="[3]"
    ),
    "GLASS_SOUL": ChallengeModifier(
        key="GLASS_SOUL",
        name="Стеклянная Душа (Хрупкая Плоть)",
        icon="✦",
        color=(255, 90, 90),
        short_tag="30 HP MAX",
        desc="Здоровье ограничено 30 HP! Любая ошибка может стать смертельной.",
        penalty_desc="Максимальное HP = 30 единиц. Запрет на увеличение запаса жизни.",
        hotkey="[4]"
    ),
    "PITCH_DARKNESS": ChallengeModifier(
        key="PITCH_DARKNESS",
        name="Вечный Мрак Бездны (Слепота)",
        icon="🌑",
        color=(190, 110, 235),
        short_tag="СЖАТЫЙ СВЕТ",
        desc="Радиус факела сжат на 55%. Враги и снаряды выскакивают прямо из тьмы.",
        penalty_desc="Радиус видимости 100 px вместо 250 px. Атмосфера плотной темноты.",
        hotkey="[5]"
    ),
    "TITAN_FRENZY": ChallengeModifier(
        key="TITAN_FRENZY",
        name="Безумие Титанов (Ярость Врагов)",
        icon="⚔",
        color=(255, 60, 60),
        short_tag="+35% СКОРОСТЬ ВРАГОВ",
        desc="Все враги: +35% скорости, +40% урона. Передышка боссов урезана вдвое!",
        penalty_desc="Скорость врагов x1.35, урон x1.40. Окно истощения боссов до 1.2s.",
        hotkey="[6]"
    ),
    "BLOOD_TAX": ChallengeModifier(
        key="BLOOD_TAX",
        name="Кровавая Расплата за Магию",
        icon="🩸",
        color=(220, 40, 80),
        short_tag="-1.5 HP ЗА КАСТ",
        desc="Черчение знака или каст заклинания требует жертвы: -1.5 HP за активацию!",
        penalty_desc="Магия истощает кровь. Черти только выверенные мощные комбо.",
        hotkey="[7]"
    )
}

CHALLENGE_ORDER = [
    "ONLY_CURSES",
    "HYPER_ADAPTATION",
    "DOOM_TIMER",
    "GLASS_SOUL",
    "PITCH_DARKNESS",
    "TITAN_FRENZY",
    "BLOOD_TAX"
]

class ChallengeManager:
    def __init__(self):
        self.active_keys = set()

    def is_active(self, key: str) -> bool:
        return key in self.active_keys

    def toggle(self, key: str):
        if key in CHALLENGES:
            if key in self.active_keys:
                self.active_keys.remove(key)
            else:
                self.active_keys.add(key)

    def enable(self, key: str):
        if key in CHALLENGES:
            self.active_keys.add(key)

    def disable(self, key: str):
        if key in self.active_keys:
            self.active_keys.remove(key)

    def enable_all(self):
        self.active_keys = set(CHALLENGE_ORDER)

    def disable_all(self):
        self.active_keys.clear()

    def apply_preset_only_curses(self):
        """Preset: Only Debuffs (Zero Buffs) + Doom Timer."""
        self.active_keys = {"ONLY_CURSES", "DOOM_TIMER"}

    def apply_preset_titan_hell(self):
        """Preset: Titan Frenzy + Hyper Adaptation."""
        self.active_keys = {"TITAN_FRENZY", "HYPER_ADAPTATION"}

    def apply_preset_glass_nightmare(self):
        """Preset: Glass Soul + Pitch Darkness + Blood Tax."""
        self.active_keys = {"GLASS_SOUL", "PITCH_DARKNESS", "BLOOD_TAX"}

    def get_active_count(self) -> int:
        return len(self.active_keys)

    def get_badge_text(self) -> str:
        if not self.active_keys:
            return ""
        return f"+ ☠ {len(self.active_keys)} УСЛОЖН."

    def get_summary_list(self):
        return [CHALLENGES[k] for k in CHALLENGE_ORDER if k in self.active_keys]

    def reset_run_stats(self):
        """Resets per-run tracking metrics for challenges if needed."""
        pass

    def modify_player_on_start(self, player):
        """Applies starting stats and restrictions according to active challenges."""
        if self.is_active("GLASS_SOUL"):
            player.max_hp = 30
            player.hp = 30

    def on_player_damage_taken(self, game, damage):
        """Triggers penalty effects when player is struck."""
        if self.is_active("DOOM_TIMER") and damage > 0:
            penalty = 6.0
            game.zone_timer = max(1.0, game.zone_timer - penalty)
            game.fx.add_floating_text(f"-{penalty:.1f}s РОК ТАЙМЕРА!", game.player.x, game.player.y - 45, (255, 80, 50), size=22)

    def on_glyph_drawn(self, game):
        """Triggers penalty effects when player executes a magic rune."""
        if self.is_active("BLOOD_TAX"):
            tax = 1.5
            game.player.hp = max(1.0, game.player.hp - tax)
            game.fx.add_floating_text(f"-{tax:.1f} HP ЖЕРТВА КРОВИ", game.player.x, game.player.y - 30, (255, 50, 80), size=18)

    def get_light_radius(self, base_radius=220):
        if self.is_active("PITCH_DARKNESS"):
            return 100
        return base_radius

    def get_enemy_speed_mult(self):
        if self.is_active("TITAN_FRENZY"):
            return 1.35
        return 1.0

    def get_enemy_damage_mult(self):
        if self.is_active("TITAN_FRENZY"):
            return 1.40
        return 1.0

    def get_boss_exhaustion_time(self, base_time=3.0):
        if self.is_active("TITAN_FRENZY"):
            return 1.2
        return base_time

    def get_spam_thresholds(self, normal_base=4, boss_base=3):
        if self.is_active("HYPER_ADAPTATION"):
            return 2, 1
        return normal_base, boss_base

    def should_offer_only_curses(self) -> bool:
        return self.is_active("ONLY_CURSES")


CHALLENGE_MANAGER = ChallengeManager()
