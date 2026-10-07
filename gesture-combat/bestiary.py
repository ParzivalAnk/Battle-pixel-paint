"""
Bestiary of 40 unique dark fantasy enemies across 5 factions.
Each enemy has unique attributes, combat behavior, abilities, and visual scaling.
"""

BESTIARY = {
    # =========================================================================
    # ФРАКЦИЯ 1: КУЛЬТ КРОВИ (Blood Cult)
    # =========================================================================
    "cult_neophyte": {
        "id": "cult_neophyte",
        "name": "Послушник Крови",
        "faction": "Культ Крови",
        "sprite_base": "cultist",
        "tint": (220, 140, 140),
        "scale": 0.85,
        "hp": 95,
        "speed": 135,
        "damage": 16,
        "attack_type": "melee",
        "special": "blood_dart", # бросает сгусток крови
        "desc": "Младший аколит, готовый пролить чужую и свою кровь."
    },
    "cult_zealot": {
        "id": "cult_zealot",
        "name": "Алый Фанатик",
        "faction": "Культ Крови",
        "sprite_base": "cultist",
        "tint": (255, 60, 60),
        "scale": 0.95,
        "hp": 130,
        "speed": 185,
        "damage": 22,
        "attack_type": "melee_rush",
        "special": "frenzy", # ускорение при получении урона
        "desc": "Слепо бросается вперед в экстазе мученичества."
    },
    "blood_inquisitor": {
        "id": "blood_inquisitor",
        "name": "Кровавый Инквизитор",
        "faction": "Культ Крови",
        "sprite_base": "inquisitor",
        "tint": (255, 255, 255),
        "scale": 1.05,
        "hp": 175,
        "speed": 160,
        "damage": 28,
        "attack_type": "dual_slash",
        "special": "dash_strike", # рывок сквозь игрока
        "desc": "Мастер парных окровавленных клинков."
    },
    "crimson_executioner": {
        "id": "crimson_executioner",
        "name": "Палач Багрового Клейма",
        "faction": "Культ Крови",
        "sprite_base": "inquisitor",
        "tint": (160, 20, 30),
        "scale": 1.30,
        "hp": 260,
        "speed": 105,
        "damage": 42,
        "attack_type": "heavy_cleave",
        "special": "ground_slam", # сокрушающий слэм со станом
        "desc": "Тяжеловооруженный каратель, разрубающий надвое."
    },
    "bishop_of_agony": {
        "id": "bishop_of_agony",
        "name": "Епископ Мучеников",
        "faction": "Культ Крови",
        "sprite_base": "cultist",
        "tint": (255, 215, 80),
        "scale": 1.10,
        "hp": 190,
        "speed": 115,
        "damage": 20,
        "attack_type": "curse_caster",
        "special": "blood_heal", # аура исцеления союзников
        "desc": "Освящает бой кровавыми песнопениями."
    },
    "shadow_drinker": {
        "id": "shadow_drinker",
        "name": "Кровопийца Тени",
        "faction": "Культ Крови",
        "sprite_base": "stalker",
        "tint": (190, 40, 80),
        "scale": 1.0,
        "hp": 150,
        "speed": 175,
        "damage": 24,
        "attack_type": "vampiric",
        "special": "lifesteal", # восстанавливает HP при ударе
        "desc": "Ненасытное создание, пожирающее жизненную силу."
    },
    "possessed_monk": {
        "id": "possessed_monk",
        "name": "Одержимый Монах",
        "faction": "Культ Крови",
        "sprite_base": "cultist",
        "tint": (140, 80, 180),
        "scale": 1.0,
        "hp": 160,
        "speed": 170,
        "damage": 26,
        "attack_type": "combo_fist",
        "special": "teleport_behind", # короткий блинк за спину
        "desc": "Тело монаха контролирует древний демон гнева."
    },
    "grand_inquisitor_malchor": {
        "id": "grand_inquisitor_malchor",
        "name": "Верховный Инквизитор Малхор [БОСС]",
        "faction": "Культ Крови",
        "sprite_base": "inquisitor",
        "tint": (255, 30, 30),
        "scale": 1.45,
        "hp": 480,
        "speed": 165,
        "damage": 45,
        "attack_type": "boss_blood",
        "special": "crimson_cross", # выпускает крест из крови
        "desc": "Глава святого трибунала, предавший душу крови."
    },

    # =========================================================================
    # ФРАКЦИЯ 2: ТИТАНЫ И ГОЛЕМЫ (Colossi & Titans)
    # =========================================================================
    "stone_sentry": {
        "id": "stone_sentry",
        "name": "Каменный Страж",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (160, 165, 175),
        "scale": 1.25,
        "hp": 240,
        "speed": 85,
        "damage": 30,
        "attack_type": "slam",
        "special": "shield_bash",
        "desc": "Древняя статуя, оживленная эфиром."
    },
    "magma_golem": {
        "id": "magma_golem",
        "name": "Магматический Голем",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (255, 120, 30),
        "scale": 1.50,
        "hp": 320,
        "speed": 90,
        "damage": 38,
        "attack_type": "fire_punch",
        "special": "lava_trail", # оставляет огненный след
        "desc": "Раскаленное ядро плавит камень вокруг него."
    },
    "obsidian_juggernaut": {
        "id": "obsidian_juggernaut",
        "name": "Обсидиановый Джаггернаут",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (70, 75, 95),
        "scale": 1.65,
        "hp": 400,
        "speed": 75,
        "damage": 46,
        "attack_type": "crush",
        "special": "armor_plating", # снижает входящий урон на 30%
        "desc": "Непробиваемая броня из вулканического стекла."
    },
    "fissure_breaker": {
        "id": "fissure_breaker",
        "name": "Разрушитель Разломов",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (210, 160, 80),
        "scale": 1.40,
        "hp": 280,
        "speed": 95,
        "damage": 35,
        "attack_type": "shockwave",
        "special": "earth_crack",
        "desc": "Раскалывает пол арены ударами кулаков."
    },
    "quake_titan": {
        "id": "quake_titan",
        "name": "Титан Землетрясения",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (180, 110, 60),
        "scale": 1.70,
        "hp": 380,
        "speed": 80,
        "damage": 44,
        "attack_type": "heavy_slam",
        "special": "screen_rumble",
        "desc": "Его поступь сотрясает подземелье."
    },
    "runic_automaton": {
        "id": "runic_automaton",
        "name": "Рунический Автоматон",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (80, 220, 255),
        "scale": 1.35,
        "hp": 260,
        "speed": 110,
        "damage": 32,
        "attack_type": "arcane_blast",
        "special": "beam_fire",
        "desc": "Механический конструкт с эфирным ядром."
    },
    "crystal_colossus": {
        "id": "crystal_colossus",
        "name": "Кристаллический Колосс",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (170, 120, 255),
        "scale": 1.55,
        "hp": 350,
        "speed": 85,
        "damage": 40,
        "attack_type": "crystal_cleave",
        "special": "crystal_spikes",
        "desc": "Искрится острыми кристаллами эфира."
    },
    "goliath_prime_titan": {
        "id": "goliath_prime_titan",
        "name": "Голиаф Первородный Титан [ГИГАНТ-БОСС]",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (255, 90, 40),
        "scale": 2.20, # НАСТОЯЩИЙ ГИГАНТ!
        "hp": 850,
        "speed": 70,
        "damage": 65,
        "attack_type": "colossal_crush",
        "special": "apocalypse_stomp",
        "desc": "Колоссальный древний исполин, возвышающийся над ареной."
    },

    # =========================================================================
    # ФРАКЦИЯ 3: НЕКРОМАНТИЯ И СКВЕРНА (Undead & Liches)
    # =========================================================================
    "plague_skeleton": {
        "id": "plague_skeleton",
        "name": "Чумной Скелет",
        "faction": "Некромантия",
        "sprite_base": "cultist",
        "tint": (100, 220, 100),
        "scale": 0.90,
        "hp": 110,
        "speed": 140,
        "damage": 18,
        "attack_type": "poison_poke",
        "special": "poison_cloud",
        "desc": "Кости сочатся ядом скверны."
    },
    "bone_legionnaire": {
        "id": "bone_legionnaire",
        "name": "Костяной Легионер",
        "faction": "Некромантия",
        "sprite_base": "inquisitor",
        "tint": (210, 215, 200),
        "scale": 1.05,
        "hp": 170,
        "speed": 125,
        "damage": 24,
        "attack_type": "shielded_thrust",
        "special": "bone_guard",
        "desc": "Дисциплинированный воин древней погребенной армии."
    },
    "crypt_wraith": {
        "id": "crypt_wraith",
        "name": "Призрак Гробницы",
        "faction": "Некромантия",
        "sprite_base": "lich",
        "tint": (130, 240, 230),
        "scale": 1.0,
        "hp": 140,
        "speed": 165,
        "damage": 22,
        "attack_type": "frost_drain",
        "special": "ghost_phase", # проходит сквозь колонны
        "desc": "Бестелесный дух, крадущий тепло живых."
    },
    "rot_bomber": {
        "id": "rot_bomber",
        "name": "Трупный Взрыватель",
        "faction": "Некромантия",
        "sprite_base": "cultist",
        "tint": (160, 230, 60),
        "scale": 0.95,
        "hp": 120,
        "speed": 195,
        "damage": 45,
        "attack_type": "suicide_charge",
        "special": "necro_detonation",
        "desc": "Раздутое тело готово взорваться кислотой."
    },
    "lich_archivist": {
        "id": "lich_archivist",
        "name": "Лич-Архивариус",
        "faction": "Некромантия",
        "sprite_base": "lich",
        "tint": (100, 255, 160),
        "scale": 1.15,
        "hp": 220,
        "speed": 105,
        "damage": 34,
        "attack_type": "skull_orb",
        "special": "soul_volley",
        "desc": "Хранитель запретных свитков смерти."
    },
    "death_knight": {
        "id": "death_knight",
        "name": "Рыцарь Смерти",
        "faction": "Некромантия",
        "sprite_base": "inquisitor",
        "tint": (80, 140, 200),
        "scale": 1.25,
        "hp": 290,
        "speed": 130,
        "damage": 38,
        "attack_type": "frost_blade",
        "special": "winter_aura", # аура замедления вокруг
        "desc": "Падший паладин на службе вечного холода."
    },
    "banshee_screamer": {
        "id": "banshee_screamer",
        "name": "Банши Смертного Вопля",
        "faction": "Некромантия",
        "sprite_base": "lich",
        "tint": (240, 160, 255),
        "scale": 1.05,
        "hp": 160,
        "speed": 155,
        "damage": 26,
        "attack_type": "scream_aoe",
        "special": "deafen_stun",
        "desc": "Ее вопль оглушает разум и парализует руки."
    },
    "archlich_mordecai": {
        "id": "archlich_mordecai",
        "name": "Архилич Мордекай [БОСС]",
        "faction": "Некромантия",
        "sprite_base": "lich",
        "tint": (80, 255, 120),
        "scale": 1.45,
        "hp": 520,
        "speed": 120,
        "damage": 48,
        "attack_type": "lich_barrage",
        "special": "bone_cage",
        "desc": "Владыка некрополя, повелевающий призраками."
    },

    # =========================================================================
    # ФРАКЦИЯ 4: ПОРОЖДЕНИЯ БЕЗДНЫ (Voidspawn & Shadows)
    # =========================================================================
    "void_stalker": {
        "id": "void_stalker",
        "name": "Сталкер Пустоты",
        "faction": "Порождения Бездны",
        "sprite_base": "stalker",
        "tint": (180, 80, 240),
        "scale": 1.05,
        "hp": 160,
        "speed": 175,
        "damage": 26,
        "attack_type": "dual_scythe",
        "special": "void_invis", # кратковременная невидимость
        "desc": "Тени смыкаются вокруг его клинков."
    },
    "shadow_skitterer": {
        "id": "shadow_skitterer",
        "name": "Теневой Прыгун",
        "faction": "Порождения Бездны",
        "sprite_base": "stalker",
        "tint": (90, 50, 130),
        "scale": 0.85,
        "hp": 115,
        "speed": 210,
        "damage": 20,
        "attack_type": "rapid_poke",
        "special": "dodge_flicker",
        "desc": "Мгновенно мечется из угла в угол арены."
    },
    "mind_flayer": {
        "id": "mind_flayer",
        "name": "Пожиратель Разума",
        "faction": "Порождения Бездны",
        "sprite_base": "cultist",
        "tint": (160, 60, 220),
        "scale": 1.15,
        "hp": 210,
        "speed": 120,
        "damage": 30,
        "attack_type": "tentacle_grab",
        "special": "mind_pull", # притягивает игрока к себе
        "desc": "Психический импульс затуманивает взор."
    },
    "aether_phantom": {
        "id": "aether_phantom",
        "name": "Эфирный Фантом",
        "faction": "Порождения Бездны",
        "sprite_base": "lich",
        "tint": (120, 160, 255),
        "scale": 1.10,
        "hp": 175,
        "speed": 150,
        "damage": 28,
        "attack_type": "warp_shot",
        "special": "damage_phase",
        "desc": "Мерцает между измерениями."
    },
    "abyssal_burrower": {
        "id": "abyssal_burrower",
        "name": "Червь Бездны",
        "faction": "Порождения Бездны",
        "sprite_base": "stalker",
        "tint": (60, 30, 80),
        "scale": 1.30,
        "hp": 270,
        "speed": 115,
        "damage": 36,
        "attack_type": "burrow_strike",
        "special": "ground_burst",
        "desc": "Выныривает из каменных плит прямо под ногами."
    },
    "shadow_marksman": {
        "id": "shadow_marksman",
        "name": "Теневой Стрелок",
        "faction": "Порождения Бездны",
        "sprite_base": "inquisitor",
        "tint": (110, 80, 170),
        "scale": 1.0,
        "hp": 140,
        "speed": 135,
        "damage": 25,
        "attack_type": "dark_arrow",
        "special": "snipe",
        "desc": "Стреляет стрелами мрака из укрытия."
    },
    "maw_demon": {
        "id": "maw_demon",
        "name": "Демон Чрева",
        "faction": "Порождения Бездны",
        "sprite_base": "golem",
        "tint": (120, 40, 60),
        "scale": 1.35,
        "hp": 310,
        "speed": 105,
        "damage": 40,
        "attack_type": "chomp",
        "special": "stamina_drain",
        "desc": "Сплошная пасть из острых зубьев."
    },
    "void_overlord": {
        "id": "void_overlord",
        "name": "Повелитель Бездны [БОСС]",
        "faction": "Порождения Бездны",
        "sprite_base": "stalker",
        "tint": (220, 60, 255),
        "scale": 1.60,
        "hp": 550,
        "speed": 150,
        "damage": 52,
        "attack_type": "void_rift",
        "special": "singularity_storm",
        "desc": "Воплощение самой пустоты, искажающее свет."
    },

    # =========================================================================
    # ФРАКЦИЯ 5: ЭЛЕМЕНТАЛИ И АНОМАЛИИ (Elementals & Anomalies)
    # =========================================================================
    "ember_wisp": {
        "id": "ember_wisp",
        "name": "Огненный Висп",
        "faction": "Стихии Хаоса",
        "sprite_base": "cultist",
        "tint": (255, 140, 40),
        "scale": 0.75,
        "hp": 85,
        "speed": 215,
        "damage": 18,
        "attack_type": "fire_spin",
        "special": "scorch_burst",
        "desc": "Пляшущий сгусток яростного пламени."
    },
    "frost_shardling": {
        "id": "frost_shardling",
        "name": "Ледяной Кристаллид",
        "faction": "Стихии Хаоса",
        "sprite_base": "stalker",
        "tint": (140, 230, 255),
        "scale": 0.85,
        "hp": 110,
        "speed": 160,
        "damage": 20,
        "attack_type": "ice_barb",
        "special": "chill_touch",
        "desc": "Острый кристалл, замораживающий при касании."
    },
    "spark_elemental": {
        "id": "spark_elemental",
        "name": "Грозовой Дух",
        "faction": "Стихии Хаоса",
        "sprite_base": "lich",
        "tint": (255, 255, 100),
        "scale": 0.95,
        "hp": 130,
        "speed": 190,
        "damage": 24,
        "attack_type": "lightning_zap",
        "special": "shock_chain",
        "desc": "Искрится неконтролируемым напряжением."
    },
    "acid_slime": {
        "id": "acid_slime",
        "name": "Токсичный Слизень",
        "faction": "Стихии Хаоса",
        "sprite_base": "cultist",
        "tint": (80, 255, 60),
        "scale": 1.10,
        "hp": 180,
        "speed": 100,
        "damage": 22,
        "attack_type": "slime_spit",
        "special": "split_on_death", # разделяется на мелких
        "desc": "Растворяет броню едкой кислотой."
    },
    "gravity_oculus": {
        "id": "gravity_oculus",
        "name": "Гравитационный Окулус",
        "faction": "Стихии Хаоса",
        "sprite_base": "lich",
        "tint": (180, 70, 220),
        "scale": 1.20,
        "hp": 230,
        "speed": 105,
        "damage": 32,
        "attack_type": "gravity_beam",
        "special": "orbit_push",
        "desc": "Левитирующее око, искривляющее законы тяготения."
    },
    "lodestone_golem": {
        "id": "lodestone_golem",
        "name": "Магнитный Страж",
        "faction": "Стихии Хаоса",
        "sprite_base": "golem",
        "tint": (120, 170, 220),
        "scale": 1.45,
        "hp": 340,
        "speed": 90,
        "damage": 36,
        "attack_type": "magnetic_slam",
        "special": "weapon_attract",
        "desc": "Притягивает металлические клинки к своему телу."
    },
    "plasma_vortex_entity": {
        "id": "plasma_vortex_entity",
        "name": "Плазменный Вихрь",
        "faction": "Стихии Хаоса",
        "sprite_base": "lich",
        "tint": (255, 80, 180),
        "scale": 1.25,
        "hp": 260,
        "speed": 135,
        "damage": 38,
        "attack_type": "plasma_flame",
        "special": "fire_tornado",
        "desc": "Бушующий ураган чистой плазмы."
    },
    "avatar_of_chaos": {
        "id": "avatar_of_chaos",
        "name": "Аватар Первородного Хаоса [БОСС]",
        "faction": "Стихии Хаоса",
        "sprite_base": "golem",
        "tint": (255, 230, 80),
        "scale": 1.80,
        "hp": 650,
        "speed": 115,
        "damage": 55,
        "attack_type": "chaos_barrage",
        "special": "elemental_shift",
        "desc": "Повелитель всех стихий, меняющий ауры на ходу."
    },
    "bladesovereign_valeria": {
        "id": "bladesovereign_valeria",
        "name": "Владычица Клинков Валерия [БОСС]",
        "faction": "Культ Крови",
        "sprite_base": "inquisitor",
        "tint": (255, 45, 120),
        "scale": 1.35,
        "hp": 580,
        "speed": 210,
        "damage": 44,
        "attack_type": "boss_blades",
        "special": "omnislash_combo",
        "desc": "Смертоносная мечница, рассекающая плоть быстрее звука."
    },
    "abyssal_drakon_nadir": {
        "id": "abyssal_drakon_nadir",
        "name": "Древний Змей Бездны Надир [БОСС]",
        "faction": "Титаны Бездны",
        "sprite_base": "golem",
        "tint": (90, 60, 190),
        "scale": 1.75,
        "hp": 880,
        "speed": 105,
        "damage": 52,
        "attack_type": "boss_drake",
        "special": "void_breath",
        "desc": "Первородный колосс глубин, изрыгающий черные дыры и гравитационные волны."
    },
    "judge_of_truth": {
        "id": "judge_of_truth",
        "name": "Верховный Судия Истины [БОСС 50 ЭТАЖА]",
        "faction": "Суд Судеб",
        "sprite_base": "inquisitor",
        "tint": (255, 215, 60),
        "scale": 1.65,
        "hp": 1500,
        "speed": 175,
        "damage": 55,
        "attack_type": "divine_verdict",
        "special": "truth_inquisition",
        "desc": "Хранитель 50-го эшелона. Взвешивает душу смертного на священных Весах Истины и беспощадно карает за ложь."
    }
}


