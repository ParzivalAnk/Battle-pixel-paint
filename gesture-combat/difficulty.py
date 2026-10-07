"""
difficulty.py - Difficulty Management for GLYPH-BLADE
Manages game difficulty levels, stat multipliers, descriptions, and modifiers.
"""

class DifficultyLevel:
    def __init__(self, key, name, icon, color, desc, player_hp, floor_timer,
                 enemy_damage_mult, enemy_speed_mult, spam_threshold_normal,
                 spam_threshold_boss, curse_chance):
        self.key = key
        self.name = name
        self.icon = icon
        self.badge = f"[{name.upper()}]"
        self.color = color
        self.desc = desc
        self.player_hp = player_hp
        self.floor_timer = floor_timer
        self.enemy_damage_mult = enemy_damage_mult
        self.enemy_speed_mult = enemy_speed_mult
        self.spam_threshold_normal = spam_threshold_normal
        self.spam_threshold_boss = spam_threshold_boss
        self.curse_chance = curse_chance

DIFFICULTIES = {
    "APPRENTICE": DifficultyLevel(
        key="APPRENTICE",
        name="Ученик",
        icon="✦",
        color=(120, 235, 160),
        desc="Для начинающих магов. Повышенный запас здоровья и времени, сниженный урон врагов.",
        player_hp=135,
        floor_timer=190.0,
        enemy_damage_mult=0.70,
        enemy_speed_mult=0.90,
        spam_threshold_normal=5,
        spam_threshold_boss=4,
        curse_chance=0.20
    ),
    "ADEPT": DifficultyLevel(
        key="ADEPT",
        name="Адепт",
        icon="⚔",
        color=(255, 215, 80),
        desc="Каноничный баланс тёмного рогалика. Враги бьют ощутимо, спам заклинаний карается адаптацией.",
        player_hp=100,
        floor_timer=150.0,
        enemy_damage_mult=1.00,
        enemy_speed_mult=1.00,
        spam_threshold_normal=4,
        spam_threshold_boss=3,
        curse_chance=0.45
    ),
    "INQUISITOR": DifficultyLevel(
        key="INQUISITOR",
        name="Инквизитор",
        icon="☠",
        color=(255, 120, 60),
        desc="Суровое испытание для ветеранов. Ошибки стоят жизни, жесткий таймер и быстрая адаптация боссов.",
        player_hp=80,
        floor_timer=120.0,
        enemy_damage_mult=1.35,
        enemy_speed_mult=1.15,
        spam_threshold_normal=3,
        spam_threshold_boss=2,
        curse_chance=0.65
    ),
    "NIGHTMARE": DifficultyLevel(
        key="NIGHTMARE",
        name="Кошмар Бездны",
        icon="❂",
        color=(235, 75, 255),
        desc="Беспощадная пучина мрака. Враги адаптируются моментально, колоссальный урон, дефицит секунд.",
        player_hp=60,
        floor_timer=90.0,
        enemy_damage_mult=1.75,
        enemy_speed_mult=1.30,
        spam_threshold_normal=2,
        spam_threshold_boss=2,
        curse_chance=0.85
    )
}

DIFFICULTY_ORDER = ["APPRENTICE", "ADEPT", "INQUISITOR", "NIGHTMARE"]

class DifficultyManager:
    def __init__(self, default_key="ADEPT"):
        self.current_key = default_key

    @property
    def current(self) -> DifficultyLevel:
        return DIFFICULTIES.get(self.current_key, DIFFICULTIES["ADEPT"])

    def set_difficulty(self, key: str):
        if key in DIFFICULTIES:
            self.current_key = key

    def cycle_next(self):
        idx = DIFFICULTY_ORDER.index(self.current_key)
        self.current_key = DIFFICULTY_ORDER[(idx + 1) % len(DIFFICULTY_ORDER)]
        return self.current

    def cycle_prev(self):
        idx = DIFFICULTY_ORDER.index(self.current_key)
        self.current_key = DIFFICULTY_ORDER[(idx - 1) % len(DIFFICULTY_ORDER)]
        return self.current

DIFFICULTY_MANAGER = DifficultyManager("ADEPT")
