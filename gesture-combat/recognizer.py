import math

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def dist(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

def path_length(points):
    d = 0.0
    for i in range(1, len(points)):
        d += points[i].dist(points[i - 1])
    return d

def resample(points, n=32):
    if not points:
        return []
    if len(points) == 1:
        return [Point(points[0].x, points[0].y) for _ in range(n)]

    total_len = path_length(points)
    if total_len == 0:
        return [Point(points[0].x, points[0].y) for _ in range(n)]

    interval = total_len / (n - 1)
    new_points = [Point(points[0].x, points[0].y)]
    curr_dist = 0.0

    i = 1
    p_prev = points[0]
    while i < len(points):
        p_curr = points[i]
        d = p_prev.dist(p_curr)
        if curr_dist + d >= interval:
            t = (interval - curr_dist) / d
            qx = p_prev.x + t * (p_curr.x - p_prev.x)
            qy = p_prev.y + t * (p_curr.y - p_prev.y)
            q = Point(qx, qy)
            new_points.append(q)
            p_prev = q
            curr_dist = 0.0
        else:
            curr_dist += d
            p_prev = p_curr
            i += 1

    while len(new_points) < n:
        new_points.append(Point(points[-1].x, points[-1].y))
    return new_points[:n]

def bounding_box(points):
    min_x = min(p.x for p in points)
    max_x = max(p.x for p in points)
    min_y = min(p.y for p in points)
    max_y = max(p.y for p in points)
    return min_x, min_y, max_x, max_y

def scale_and_center(points, target_size=100.0):
    min_x, min_y, max_x, max_y = bounding_box(points)
    w = max(max_x - min_x, 1.0)
    h = max(max_y - min_y, 1.0)
    
    scale = target_size / max(w, h)
    scaled = [Point(p.x * scale, p.y * scale) for p in points]
        
    cx = sum(p.x for p in scaled) / len(scaled)
    cy = sum(p.y for p in scaled) / len(scaled)
    
    return [Point(p.x - cx, p.y - cy) for p in scaled]

def gesture_distance(pts1, pts2):
    d = 0.0
    for p1, p2 in zip(pts1, pts2):
        d += p1.dist(p2)
    return d / len(pts1)

# Template Library
TEMPLATES = {}

def add_template(name, raw_points):
    pts = [Point(x, y) for x, y in raw_points]
    resampled = resample(pts, 32)
    normalized = scale_and_center(resampled, 100.0)
    TEMPLATES[name] = normalized

# 1. Horizontal Slashes (—)
add_template("SLASH_H_R", [(0, 50), (25, 50), (50, 50), (75, 50), (100, 50)])
add_template("SLASH_H_L", [(100, 50), (75, 50), (50, 50), (25, 50), (0, 50)])

# 2. Vertical Overhead Slam (|)
add_template("SLASH_V", [(50, 0), (50, 25), (50, 50), (50, 75), (50, 100)])

# 3. Uppercut / Launcher (^)
add_template("UPPERCUT", [(10, 90), (30, 50), (50, 10), (70, 50), (90, 90)])
add_template("UPPERCUT_SLASH", [(50, 100), (50, 75), (50, 50), (50, 25), (50, 0)])

# 4. Parry Stance (V)
add_template("PARRY", [(10, 10), (30, 50), (50, 90), (70, 50), (90, 10)])

# 5. Thrust / Spear Poke (>)
add_template("THRUST", [(20, 10), (55, 30), (90, 50), (55, 70), (20, 90)])

# 6. Whirlwind Circle (O)
circle_cw = []
circle_ccw = []
for i in range(16):
    angle = -math.pi/2 + (2 * math.pi * i / 15)
    circle_cw.append((50 + 45 * math.cos(angle), 50 + 45 * math.sin(angle)))
    angle_ccw = -math.pi/2 - (2 * math.pi * i / 15)
    circle_ccw.append((50 + 45 * math.cos(angle_ccw), 50 + 45 * math.sin(angle_ccw)))
add_template("CIRCLE_CW", circle_cw)
add_template("CIRCLE_CCW", circle_ccw)

# 7. Lightning Dash (Z)
add_template("ZIGZAG", [(10, 15), (50, 15), (90, 15), (50, 50), (10, 85), (50, 85), (90, 85)])

# 8. Pentagonal Shield / Fist Block (Рисуется: Верхняя планка -> Вниз направо -> Острие внизу -> Вверх налево -> Замыкание вверху)
add_template("SHIELD_BLOCK", [
    (20, 20), (50, 20), (80, 20),
    (80, 50), (80, 65),
    (50, 95),
    (20, 65), (20, 50),
    (20, 20)
])

# 9. Hourglass / Shadow Swap (Песочные часы: Верх -> Диагональ в правый низ -> Влево -> Диагональ в правый верх)
add_template("HOURGLASS_SWAP", [
    (20, 20), (50, 20), (80, 20),
    (50, 52),
    (20, 85), (50, 85), (80, 85),
    (50, 52),
    (20, 20)
])

# 10. 5-Point Star / Pentagram (Пятиконечная звезда судного дня)
add_template("STAR_PENTAGRAM", [
    (50, 10),
    (80, 90),
    (10, 40),
    (90, 40),
    (20, 90),
    (50, 10)
])

# 11. Cross / X-Slash [X] (Крестовой разрез - два диагональных росчерка unistroke)
add_template("CROSS", [
    (15, 15), (50, 50), (85, 85),
    (85, 15), (50, 50), (15, 85)
])
add_template("CROSS_ALT", [
    (15, 85), (50, 50), (85, 15),
    (15, 15), (50, 50), (85, 85)
])

# 12. Prismatic Triangle [△] (Призматический треугольник / Эгида)
add_template("TRIANGLE", [
    (50, 10), (90, 85), (10, 85), (50, 10)
])

# 13. Infinity Loop [∞] (Петля бесконечности - омнислеш)
infinity_pts = []
for i in range(24):
    t = -math.pi/2 + (2 * math.pi * i / 23)
    # Lemniscate of Bernoulli or figure-8
    ix = 50 + 40 * math.sin(t)
    iy = 50 + 25 * math.sin(2 * t)
    infinity_pts.append((ix, iy))
add_template("INFINITY", infinity_pts)

def register_custom_glyph(raw_points, name="CUSTOM_GLYPH"):
    """Registers user-drawn custom glyph template at runtime."""
    add_template(name, raw_points)


# Ability registry mapping gesture shapes to unique abilities
SKILL_INFO = {
    "SHIELD_BLOCK": {
        "name": "Блок Бастиона / Slo-Mo",
        "symbol": "🛡",
        "description": "Стойка скрещенных кулаков/щита. Блокирует урон и ВКЛЮЧАЕТ ЗАМЕДЛЕНИЕ ВРЕМЕНИ (Slo-Mo x5) на 3 сек!",
        "base_damage": 0,
        "type": "shield_block",
        "color": (255, 220, 60)
    },
    "HOURGLASS_SWAP": {
        "name": "Теневая Рокировка",
        "symbol": "⌛",
        "description": "Мгновенно меняет тебя и врага местами! Враг бьет в пустоту, а ты заходишь в спину (BACKSTAB +200%)!",
        "base_damage": 40,
        "type": "swap_position",
        "color": (210, 100, 255)
    },
    "STAR_PENTAGRAM": {
        "name": "Звезда Катаклизма",
        "symbol": "★",
        "description": "Сложнейшая пятиконечная печать. Вызывает колоссальный взрыв судного дня на всю арену!",
        "base_damage": 180,
        "type": "cataclysm_star",
        "color": (255, 50, 50)
    },
    "SLASH_H": {
        "name": "Пространственный Срез",
        "symbol": "—",
        "description": "Телепортирующий разрез сквозь ткань пространства. Мгновенно рассекает врагов.",
        "base_damage": 45,
        "type": "dimensional_slash",
        "color": (120, 240, 255)
    },
    "SLASH_V": {
        "name": "Падение Метеорита",
        "symbol": "|",
        "description": "Обрушивает пылающий астероид с небес в точку прицела. Дробит замерзших врагов в пыль (Shatter x2.5)!",
        "base_damage": 95,
        "type": "meteor",
        "color": (255, 90, 30)
    },
    "UPPERCUT": {
        "name": "Инфернальный Разлом",
        "symbol": "^",
        "description": "Волна яростного огня вырывается из земли конусом, поджигая плоть.",
        "base_damage": 60,
        "type": "fire_fissure",
        "color": (255, 170, 40)
    },
    "PARRY": {
        "name": "Ледяной Стазис",
        "symbol": "V",
        "description": "Ледяные кристаллические шипы замуровывают врага в неподвижную ледяную глыбу!",
        "base_damage": 30,
        "type": "frost_stasis",
        "color": (140, 230, 255)
    },
    "CIRCLE": {
        "name": "Сингулярность Бездны",
        "symbol": "O",
        "description": "Создает Черную Дыру, которая стягивает всех врагов в эпицентр, а затем схлопывается взрывом!",
        "base_damage": 80,
        "type": "vortex",
        "color": (180, 80, 255)
    },
    "ZIGZAG": {
        "name": "Цепная Молния",
        "symbol": "Z",
        "description": "Грозовой разряд поражает цель и скачет между всеми врагами на арене, парализуя их током!",
        "base_damage": 50,
        "type": "lightning",
        "color": (255, 255, 100)
    },
    "CROSS": {
        "name": "Крестовой Разруб",
        "symbol": "X",
        "description": "Два скрещенных лезвия бьют в одну точку. Колоссальный урон и пробитие брони!",
        "base_damage": 90,
        "type": "cross_slash",
        "color": (255, 60, 110)
    },
    "TRIANGLE": {
        "name": "Эгида Призмы",
        "symbol": "△",
        "description": "Призматический кинетический барьер. Отбрасывает врагов и поглощает урон боссов!",
        "base_damage": 45,
        "type": "prismatic_barrier",
        "color": (100, 255, 200)
    },
    "INFINITY": {
        "name": "Петля Бесконечности",
        "symbol": "∞",
        "description": "Серия из 10 фантомных клинковых срезов вокруг игрока (Omnislash)!",
        "base_damage": 135,
        "type": "infinite_barrage",
        "color": (220, 120, 255)
    },
    "CUSTOM_GLYPH": {
        "name": "Знак Владыки (Кастомный)",
        "symbol": "✦",
        "description": "Твой собственный нарисованный знак! Сверхкритический урон x3 и оглушение!",
        "base_damage": 160,
        "type": "custom_strike",
        "color": (255, 235, 90)
    }
}

def evaluate_gesture(raw_points):
    """
    Evaluates raw mouse points.
    Returns:
      (skill_id, accuracy_float, quality_tier, deviation_deg)
      quality_tier: 'PERFECT', 'CLEAN', 'SLOPPY', 'FUMBLE'
    """
    if len(raw_points) < 2:
        return None, 0.0, "INVALID", 0.0

    pts = [Point(x, y) for x, y in raw_points]
    if path_length(pts) < 18.0:
        return None, 0.0, "INVALID", 0.0

    resampled = resample(pts, 32)
    normalized = scale_and_center(resampled, 100.0)

    best_name = None
    best_dist = float('inf')

    for name, template in TEMPLATES.items():
        d = gesture_distance(normalized, template)
        if d < best_dist:
            best_dist = d
            best_name = name

    # Map sub-templates to primary skill
    skill_id = best_name
    if skill_id in ("SLASH_H_R", "SLASH_H_L"):
        skill_id = "SLASH_H"
    elif skill_id in ("UPPERCUT", "UPPERCUT_SLASH"):
        skill_id = "UPPERCUT"
    elif skill_id in ("CIRCLE_CW", "CIRCLE_CCW"):
        skill_id = "CIRCLE"
    elif skill_id == "CROSS_ALT":
        skill_id = "CROSS"

    # Calibration:
    # 0..10 dist => 98..88% (PERFECT)
    # 10..22 dist => 88..70% (CLEAN)
    # 22..38 dist => 70..50% (SLOPPY)
    # >38 dist => <50% (FUMBLE)
    score = max(0.0, min(1.0, 1.0 - (best_dist / 60.0)))

    import random
    if score >= 0.86:
        tier = "PERFECT"
        deviation = random.uniform(-1.5, 1.5)
    elif score >= 0.70:
        tier = "CLEAN"
        deviation = random.uniform(-6.0, 6.0)
    elif score >= 0.48:
        tier = "SLOPPY"
        deviation = random.uniform(-28.0, 28.0) # Noticeable deviation: high chance to miss!
    else:
        tier = "FUMBLE"
        deviation = random.uniform(-60.0, 60.0) # Total misfire / whiff

    return skill_id, score, tier, deviation
