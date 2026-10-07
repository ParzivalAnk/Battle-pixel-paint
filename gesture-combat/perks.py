"""
Portal Offerings & Cursed Pacts System for GLYPH-BLADE.
Implements:
1. Randomized pools of diverse portal choices.
2. Double-Edged Boons (1 powerful Buff + 1 impactful Debuff).
3. Cursed Boons (ONLY a debuff with purple pulsating cracked visuals).
"""

import math
import random
import pygame

TEXT_WHITE = (240, 245, 255)
TEXT_GOLD = (255, 220, 60)
TEXT_RED = (255, 80, 80)
TEXT_CYAN = (80, 225, 255)
TEXT_PURPLE = (220, 90, 255)
TEXT_GREEN = (70, 245, 125)


class PortalPerk:
    def __init__(self, perk_id, name, is_cursed, icon_symbol, buff_title, buff_desc, debuff_title, debuff_desc, apply_callback):
        self.id = perk_id
        self.name = name
        self.is_cursed = is_cursed
        self.icon_symbol = icon_symbol
        self.buff_title = buff_title
        self.buff_desc = buff_desc
        self.debuff_title = debuff_title
        self.debuff_desc = debuff_desc
        self.apply_callback = apply_callback

    def apply(self, player, game):
        self.apply_callback(player, game)
        if self.is_cursed:
            player.curse_count = getattr(player, 'curse_count', 0) + 1
            game.sfx.play("crit")
            game.fx.add_screen_shake(18.0)
            game.fx.add_floating_text(f"☠ ПРИНЯТО ПРОКЛЯТИЕ: {self.name}! ☠", player.x, player.y - 70, TEXT_PURPLE, size=26)
        else:
            game.sfx.play("parry")
            game.fx.add_screen_shake(12.0)
            game.fx.add_floating_text(f"★ ПАКТ ПРИНЯТ: {self.name}!", player.x, player.y - 70, TEXT_GOLD, size=26)


# =============================================================================
# PERK CALLBACK IMPLEMENTATIONS
# =============================================================================

def _apply_berserker(p, g):
    p.bonus_damage_mult += 0.45
    p.max_hp = max(25, p.max_hp - 25)
    p.hp = min(p.hp, p.max_hp)

def _apply_chrono_deal(p, g):
    p.bonus_time_per_floor += 45.0
    p.speed_mult = getattr(p, 'speed_mult', 1.0) * 0.82

def _apply_glass_blade(p, g):
    p.bonus_damage_mult += 0.60
    p.damage_taken_mult = getattr(p, 'damage_taken_mult', 1.0) * 1.30

def _apply_titanic_carapace(p, g):
    p.max_hp += 60
    p.hp = p.max_hp
    p.damage_taken_mult = getattr(p, 'damage_taken_mult', 1.0) * 0.82
    p.speed_mult = getattr(p, 'speed_mult', 1.0) * 0.85

def _apply_volatile_aether(p, g):
    p.bonus_damage_mult += 0.35
    p.bonus_jitter = getattr(p, 'bonus_jitter', 0.0) + 3.5

def _apply_reaper_greed(p, g):
    p.lifesteal_per_kill = getattr(p, 'lifesteal_per_kill', 0) + 7
    p.timer_drain_mult = getattr(p, 'timer_drain_mult', 1.0) * 1.25

def _apply_prismatic_singularity(p, g):
    p.slo_mo_power = getattr(p, 'slo_mo_power', 1.0) * 1.6
    p.bonus_time_per_floor -= 15.0

def _apply_infernal_combustion(p, g):
    p.bonus_damage_mult += 0.35
    p.damage_taken_mult = getattr(p, 'damage_taken_mult', 1.0) * 1.20

def _apply_glacial_freeze_pact(p, g):
    p.freeze_duration_bonus = getattr(p, 'freeze_duration_bonus', 0.0) + 2.0
    p.bonus_time_per_floor -= 20.0

def _apply_feather_step(p, g):
    p.speed_mult = getattr(p, 'speed_mult', 1.0) * 1.35
    p.max_hp = max(30, p.max_hp - 20)
    p.hp = min(p.hp, p.max_hp)

def _apply_infinite_loop_boon(p, g):
    p.bonus_damage_mult += 0.40
    p.weapon.damage_mult = max(0.4, p.weapon.damage_mult * 0.80)

def _apply_vampiric_pledge(p, g):
    p.lifesteal_percent = getattr(p, 'lifesteal_percent', 0.0) + 0.15
    p.max_hp = max(30, p.max_hp - 30)
    p.hp = min(p.hp, p.max_hp)

def _apply_cataclysm_seal(p, g):
    p.cataclysm_execute = True
    p.bonus_time_per_floor -= 15.0

def _apply_thunder_fury(p, g):
    p.bonus_damage_mult += 0.30
    p.damage_taken_mult = getattr(p, 'damage_taken_mult', 1.0) * 1.20

def _apply_heavy_fortress(p, g):
    p.damage_taken_mult = getattr(p, 'damage_taken_mult', 1.0) * 0.75
    p.speed_mult = getattr(p, 'speed_mult', 1.0) * 0.80

def _apply_fusion_mastery(p, g):
    p.fusion_damage_bonus = getattr(p, 'fusion_damage_bonus', 0.0) + 0.55
    p.timer_drain_mult = getattr(p, 'timer_drain_mult', 1.0) * 1.15


# --- Cursed Callbacks (Only Debuffs!) ---
def _apply_curse_brittle(p, g):
    p.damage_taken_mult = getattr(p, 'damage_taken_mult', 1.0) * 1.45

def _apply_curse_burning_time(p, g):
    p.timer_drain_mult = getattr(p, 'timer_drain_mult', 1.0) * 1.40

def _apply_curse_lead_veins(p, g):
    p.speed_mult = getattr(p, 'speed_mult', 1.0) * 0.75

def _apply_curse_feeble_magic(p, g):
    p.bonus_damage_mult = max(0.3, p.bonus_damage_mult * 0.68)

def _apply_curse_blind_chaos(p, g):
    p.bonus_jitter = getattr(p, 'bonus_jitter', 0.0) + 6.5

def _apply_curse_relentless_dark(p, g):
    p.damage_taken_mult = getattr(p, 'damage_taken_mult', 1.0) * 1.30
    p.timer_drain_mult = getattr(p, 'timer_drain_mult', 1.0) * 1.20

def _apply_curse_glass_heart(p, g):
    p.max_hp = max(20, p.max_hp - 25)
    p.hp = min(p.hp, p.max_hp)

def _apply_curse_mana_burn(p, g):
    p.damage_taken_mult = getattr(p, 'damage_taken_mult', 1.0) * 1.30
    p.timer_drain_mult = getattr(p, 'timer_drain_mult', 1.0) * 1.25

def _apply_curse_creeping_doom(p, g):
    p.bonus_time_per_floor -= 30.0

def _apply_curse_blood_tax(p, g):
    p.bonus_damage_mult = max(0.4, p.bonus_damage_mult * 0.75)
    p.speed_mult = getattr(p, 'speed_mult', 1.0) * 0.85


# =============================================================================
# MASTER CATALOG OF ALL OFFERINGS
# =============================================================================

DOUBLE_EDGED_PERKS = [
    PortalPerk(
        "berserker_pact", "Пакт Кровавого Берсерка", False, "⚔",
        "УРОН ВСЕХ ЗАКЛИНАНИЙ И АТАК +45%", "Наносит сокрушающий урон всем монстрам и боссам.",
        "МАКСИМАЛЬНОЕ HP -25 ЕДИНИЦ", "Твое тело истощается ради нечестивой мощи.",
        _apply_berserker
    ),
    PortalPerk(
        "chrono_deal", "Сделка с Хроносом", False, "⌛",
        "ТАЙМЕР ЭТАЖА +45 СЕКУНД", "Дополнительное время на каждом этаже подземелья.",
        "СКОРОСТЬ ПЕРЕМЕЩЕНИЯ -18%", "Течение времени замедляет твои собственные шаги.",
        _apply_chrono_deal
    ),
    PortalPerk(
        "glass_blade", "Стеклянный Клинок", False, "✦",
        "КРИТИЧЕСКИЙ УРОН И КОМБО +60%", "Каждый точный удар рассекает врагов надвое.",
        "ПОЛУЧАЕМЫЙ УРОН +30%", "Малейшая ошибка может стать смертельной.",
        _apply_glass_blade
    ),
    PortalPerk(
        "titanic_carapace", "Титанический Панцирь", False, "🛡",
        "+60 MAX HP И ПОЛНОЕ ИСЦЕЛЕНИЕ", "Колоссальный запас стойкости и жизненной силы.",
        "СКОРОСТЬ -15% И ТЯЖЕЛАЯ ИНЕРЦИЯ", "Броня титана сковывает маневренность.",
        _apply_titanic_carapace
    ),
    PortalPerk(
        "volatile_aether", "Нестабильный Эфир", False, "⚡",
        "РАДИУС И МОЩЬ ВЗРЫВОВ +40%", "Все заклинания охватывают гигантскую площадь.",
        "ПОМЕХИ КУРСОРА (JITTER +3.5)", "Хаотический эфир сотрясает руку черчения.",
        _apply_volatile_aether
    ),
    PortalPerk(
        "reaper_greed", "Алчность Жнеца Душ", False, "☠",
        "УБИЙСТВО ВРАГА ЛЕЧИТ +7 HP", "Каждая побежденная нежить восстанавливает здоровье.",
        "ТАЙМЕР ТАЕТ НА +25% БЫСТРЕЕ", "Песок времени утекает сквозь пальцы смерти.",
        _apply_reaper_greed
    ),
    PortalPerk(
        "prismatic_singularity", "Призматическая Сингулярность", False, "△",
        "SLO-MO x8 ПРИ БЛОКЕ БАСТИОНА", "Почти полная остановка мира при черчении защиты.",
        "ТАЙМЕР ЭТАЖА -15 СЕКУНД", "Манипуляции со временем сокращают срок жизни.",
        _apply_prismatic_singularity
    ),
    PortalPerk(
        "infernal_combustion", "Инфернальный Жар", False, "^",
        "ОГНЕННЫЙ УРОН И ПЕПЕЛ +75%", "Яростное пламя испепеляет ряды монстров.",
        "УРОН ОТ АТАК БОССОВ +20%", "Пламя притягивает ярость древних владык.",
        _apply_infernal_combustion
    ),
    PortalPerk(
        "glacial_freeze_pact", "Ледяное Окоченение", False, "❄",
        "ДЛИТЕЛЬНОСТЬ ЗАМОРОЗКИ +2.0 СЕК", "Монстры надолго замирают в ледяных глыбах.",
        "ТАЙМЕР ЭТАЖА -20 СЕКУНД", "Ледяной холод замораживает сами песчинки часов.",
        _apply_glacial_freeze_pact
    ),
    PortalPerk(
        "feather_step", "Танец Легкого Шага", False, "»",
        "СКОРОСТЬ ПЕРЕДВИЖЕНИЯ +35%", "Стремительные перемещения и молниеносные маневры.",
        "МАКСИМАЛЬНОЕ HP -20 ЕДИНИЦ", "Легкость достигается утратой плотности плоти.",
        _apply_feather_step
    ),
    PortalPerk(
        "infinite_loop_boon", "Петля Бесконечности", False, "∞",
        "ОМНИСЛЕШ ВЫЗЫВАЕТ НА +6 СРЕЗОВ БОЛЬШЕ", "Нескончаемый шквал призрачных световых лезвий.",
        "УРОН БАЗОВОГО ОРУЖИЯ -20%", "Сила клинка перетекает исключительно в заклинания.",
        _apply_infinite_loop_boon
    ),
    PortalPerk(
        "vampiric_pledge", "Вампирический Залог", False, ">",
        "ВАМПИРИЗМ: +15% ОТ ВСЕГО УРОНА В HP", "Непрерывное поглощение жизненных сил врагов.",
        "МАКСИМАЛЬНОЕ HP -30 ЕДИНИЦ", "Кровавая клятва укорачивает сосуд твоей души.",
        _apply_vampiric_pledge
    ),
    PortalPerk(
        "cataclysm_seal", "Печать Катаклизма", False, "★",
        "ЗВЕЗДА МГНОВЕННО КАЗНИТ ПРИ <35% HP", "Печать бездны стирает ослабленных боссов в пыль.",
        "СТАРТОВЫЙ ТАЙМЕР -15 СЕКУНД", "Катаклизм требует жертвы секундами твоей жизни.",
        _apply_cataclysm_seal
    ),
    PortalPerk(
        "thunder_fury", "Громовая Ярость", False, "Z",
        "ЦЕПНАЯ МОЛНИЯ ПОРАЖАЕТ +3 ЦЕЛИ", "Электрический разряд перескакивает через всю арену.",
        "ПОЛУЧАЕМЫЙ УРОН +20%", "Проводящее электричество тело притягивает удары.",
        _apply_thunder_fury
    ),
    PortalPerk(
        "heavy_fortress", "Бастион Несокрушимости", False, "🛡",
        "ПОГЛОЩЕНИЕ УРОНА +25%", "Удары врагов лишь со звоном отскакивают от щита.",
        "СКОРОСТЬ БЕГА И РЫВКОВ -20%", "Тяжелая каменная поступь замедляет маневры.",
        _apply_heavy_fortress
    ),
    PortalPerk(
        "fusion_mastery", "Гримуар Великого Синтеза", False, "📖",
        "УРОН СОСТАВНЫХ КОМБО (FUSIONS) +55%", "Связки двух и трех знаков разрушают саму реальность.",
        "ТАЙМЕР ТАЕТ НА +15% БЫСТРЕЕ", "Эфирное перенапряжение ускоряет ход времени.",
        _apply_fusion_mastery
    )
]

CURSED_PERKS = [
    PortalPerk(
        "curse_brittle", "Проклятие Хрупкой Плоти", True, "☠",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Бездна ничего не дает даром тем, кто оступился.",
        "ПОЛУЧАЕМЫЙ УРОН ОТ ВСЕХ АТАК +45%", "Каждый пропущенный удар рассекает тело до костей.",
        _apply_curse_brittle
    ),
    PortalPerk(
        "curse_burning_time", "Проклятие Сгорающего Времени", True, "⌛",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Темный рок не сулит благословений.",
        "ТАЙМЕР ЭТАЖА СГОРАЕТ НА +40% БЫСТРЕЕ", "Секунды улетучиваются с дикой скоростью.",
        _apply_curse_burning_time
    ),
    PortalPerk(
        "curse_lead_veins", "Проклятие Свинцовых Жил", True, "⛓",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Только путы и тяжесть загробного мира.",
        "СКОРОСТЬ ПЕРЕМЕЩЕНИЯ -25%, ТЯЖЕЛАЯ ИНЕРЦИЯ", "Ноги наливаются свинцом, уклоняться почти невозможно.",
        _apply_curse_lead_veins
    ),
    PortalPerk(
        "curse_feeble_magic", "Проклятие Бессилия Эфира", True, "✕",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Священное пламя рун угасает во мраке.",
        "УРОН ВСЕХ ЗАКЛИНАНИЙ И ОРУЖИЯ -35%", "Твои знаки теряют разрушительную мощь.",
        _apply_curse_feeble_magic
    ),
    PortalPerk(
        "curse_blind_chaos", "Проклятие Слепого Эфира", True, "👁",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Разум застилает туман первородного безумия.",
        "ДИКОЕ ДРОЖАНИЕ КУРСОРА (JITTER +6.5)", "Прицел неистово трясется от темных помех.",
        _apply_curse_blind_chaos
    ),
    PortalPerk(
        "curse_relentless_dark", "Проклятие Неумолимой Тьмы", True, "🌑",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Древние тени требуют жестокой расправы.",
        "ВРАГИ НАНОСЯТ +30% УРОНА И ТАЙМЕР +20%", "Подземелье ополчилось против тебя всей яростью.",
        _apply_curse_relentless_dark
    ),
    PortalPerk(
        "curse_glass_heart", "Проклятие Стеклянного Сердца", True, "💔",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Твоя жизненная оболочка истончается до предела.",
        "МАКСИМАЛЬНОЕ HP -25 ЕДИНИЦ", "Опасность гибели от любого шального удара возрастает.",
        _apply_curse_glass_heart
    ),
    PortalPerk(
        "curse_mana_burn", "Проклятие Сгорания Души", True, "🔥",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Пламя преисподней разъедает защитные чары.",
        "ПОЛУЧАЕМЫЙ УРОН +30% И ТАЙМЕР ТАЕТ НА +25%", "Каждое ранение отзывается жгучей болью.",
        _apply_curse_mana_burn
    ),
    PortalPerk(
        "curse_creeping_doom", "Проклятие Зыбкого Времени", True, "⏳",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Пески вечности утекают в бездну небытия.",
        "ТАЙМЕР КАЖДОГО ЭТАЖА -30 СЕКУНД", "Времени на зачистку монстров становится критически мало.",
        _apply_curse_creeping_doom
    ),
    PortalPerk(
        "curse_blood_tax", "Проклятие Истощения Жизни", True, "🩸",
        "ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", "Слабость сковывает мышцы и разум мага.",
        "УРОН -25% И СКОРОСТЬ ПЕРЕДВИЖЕНИЯ -15%", "Медленная поступь и притупленная острота рун.",
        _apply_curse_blood_tax
    )
]


def generate_portal_offerings(floor_idx=1, curse_chance=0.45, only_curses=False):
    """
    Selects 3 distinct offerings for the portal.
    If only_curses is True: rolls 100% pure Cursed Perks (0 buffs, only debuffs)!
    curse_chance controls probability of rolling a Cursed Boon (ONLY debuff).
    """
    if only_curses:
        return random.sample(CURSED_PERKS, 3)

    offerings = []
    has_curse = (random.random() < curse_chance)

    if has_curse:
        chosen_curse = random.choice(CURSED_PERKS)
        # Select 2 distinct double-edged boons
        normal_samples = random.sample(DOUBLE_EDGED_PERKS, 2)
        # Place curse at a random slot (1, 2, or 3)
        curse_slot = random.randint(0, 2)
        if curse_slot == 0:
            offerings = [chosen_curse, normal_samples[0], normal_samples[1]]
        elif curse_slot == 1:
            offerings = [normal_samples[0], chosen_curse, normal_samples[1]]
        else:
            offerings = [normal_samples[0], normal_samples[1], chosen_curse]
    else:
        offerings = random.sample(DOUBLE_EDGED_PERKS, 3)

    return offerings


# =============================================================================
# RENDERING UTILITIES: CRACKED CURSED CARD & DOUBLE-EDGED CARD
# =============================================================================

def draw_cracked_cursed_card(surface, rect, offering, anim_time, is_hovered, fonts):
    """
    Renders the Cursed Boon card:
    - Glowing, pulsating violet/purple aura.
    - Procedural jagged cracks and fracture fissures across card corners and icon.
    - Deep dark purple background with violet corruption veins.
    """
    pulse = 0.5 + 0.5 * math.sin(anim_time * 6.0)
    purple_bright = (195 + int(55 * pulse), 45, 255)
    purple_dark = (24, 6, 34)
    purple_glow = (145 + int(45 * pulse), 25, 215)

    # 1. Base Container
    pygame.draw.rect(surface, purple_dark, rect)

    # 2. Pulsating Neon Purple Borders (multiple layers for glow)
    glow_thick = 4 if is_hovered else 2
    pygame.draw.rect(surface, purple_glow, rect, glow_thick + 2)
    pygame.draw.rect(surface, purple_bright, rect, glow_thick)

    # 3. Icon Box (Left side: 68x68)
    icon_box = pygame.Rect(rect.x + 15, rect.y + 15, 68, 68)
    pygame.draw.rect(surface, (18, 5, 28), icon_box)
    pygame.draw.rect(surface, purple_bright, icon_box, 2)

    # Icon symbol (fractured skull / dark rune)
    sym_font = fonts.get("sym_large", fonts["large"])
    sym_s = sym_font.render(offering.icon_symbol, True, purple_bright)
    surface.blit(sym_s, (icon_box.centerx - sym_s.get_width() // 2, icon_box.centery - sym_s.get_height() // 2))

    # 4. Procedural Jagged Cracks & Crystal Fractures
    cx, cy = icon_box.centerx, icon_box.centery
    crack_lines = [
        # Radiating cracks through icon box and left borders
        [(cx, cy), (cx - 16, cy - 18), (icon_box.x, icon_box.y + 8), (rect.x + 4, rect.y + 12)],
        [(cx, cy), (cx - 18, cy + 16), (icon_box.x + 6, icon_box.bottom), (rect.x + 12, rect.bottom - 4)],
        [(cx, cy), (cx + 14, cy - 18), (icon_box.right, icon_box.y + 12), (icon_box.right + 26, rect.y + 4)],
        [(cx, cy), (cx + 16, cy + 18), (icon_box.right - 8, icon_box.bottom), (icon_box.right + 35, rect.bottom - 4)],
        # Top-right corner fractures
        [(rect.right - 130, rect.y + 4), (rect.right - 85, rect.y + 16), (rect.right - 35, rect.y + 10), (rect.right - 4, rect.y + 32)],
        [(rect.right - 85, rect.y + 16), (rect.right - 65, rect.y + 42), (rect.right - 4, rect.y + 55)],
        # Bottom-right corner fractures
        [(rect.right - 140, rect.bottom - 4), (rect.right - 95, rect.bottom - 20), (rect.right - 45, rect.bottom - 14), (rect.right - 4, rect.bottom - 28)],
        [(rect.right - 95, rect.bottom - 20), (rect.right - 80, rect.bottom - 46), (rect.right - 4, rect.bottom - 60)]
    ]

    for cl in crack_lines:
        # Outer purple crack glow
        pygame.draw.lines(surface, (220, 85, 255), False, cl, 3)
        # Inner white-hot fracture core
        pygame.draw.lines(surface, (255, 235, 255), False, cl, 1)

    # Glowing purple corruption fissure nodes
    fissure_nodes = [(cx, cy), (rect.right - 85, rect.y + 16), (rect.right - 95, rect.bottom - 20)]
    for nx, ny in fissure_nodes:
        pygame.draw.circle(surface, (255, 140, 255), (nx, ny), 3)
        pygame.draw.circle(surface, (255, 255, 255), (nx, ny), 1)

    # 5. Title & Status Badges
    tx = rect.x + 95
    ty = rect.y + 10

    # Skull symbol before text
    skull_sym = fonts.get("sym_med", fonts["large"]).render("☠", True, (255, 110, 240))
    surface.blit(skull_sym, (tx, ty - 2))
    tag_cursed = fonts["small"].render("ПРОКЛЯТЫЙ ДАР БЕЗДНЫ — ТОЛЬКО ДЕБАФФ!", True, (255, 110, 240))
    surface.blit(tag_cursed, (tx + skull_sym.get_width() + 6, ty))

    t_surf = fonts["large"].render(offering.name, True, purple_bright)
    surface.blit(t_surf, (tx, ty + 20))

    # 6. Buff line: explicitly absent
    b_txt = fonts["small"].render("[—] БАФФ: ОТСУТСТВУЕТ (ЧИСТОЕ ПРОКЛЯТИЕ!)", True, (140, 130, 155))
    surface.blit(b_txt, (tx, ty + 48))

    # 7. Debuff line: vibrant pulsating dark red/purple
    d_lbl = fonts["med"].render(f"▼ ДЕБАФФ: {offering.debuff_title}", True, (255, 80, 100))
    surface.blit(d_lbl, (tx, ty + 66))

    d_desc = fonts["small"].render(offering.debuff_desc, True, (245, 185, 200))
    surface.blit(d_desc, (tx, ty + 88))


def draw_double_edged_card(surface, rect, offering, anim_time, is_hovered, fonts):
    """
    Renders a standard Double-Edged Boon card:
    - Glowing cyan/gold border.
    - Green Buff line (▲).
    - Red/Orange Debuff line (▼).
    """
    bg_col = (18, 24, 38) if not is_hovered else (24, 32, 50)
    border_col = TEXT_GOLD if is_hovered else (70, 100, 150)

    pygame.draw.rect(surface, bg_col, rect)
    pygame.draw.rect(surface, border_col, rect, 2 if not is_hovered else 3)

    # Icon Box
    icon_box = pygame.Rect(rect.x + 15, rect.y + 15, 68, 68)
    pygame.draw.rect(surface, (14, 18, 28), icon_box)
    pygame.draw.rect(surface, TEXT_CYAN, icon_box, 1)

    sym_s = fonts["sym_large"].render(offering.icon_symbol, True, TEXT_CYAN)
    surface.blit(sym_s, (icon_box.centerx - sym_s.get_width() // 2, icon_box.centery - sym_s.get_height() // 2))

    tx = rect.x + 95
    ty = rect.y + 10

    tag_pact = fonts["small"].render("[ДВУЕДИНЫЙ ПАКТ: БАФФ + ДЕБАФФ]", True, TEXT_GOLD)
    surface.blit(tag_pact, (tx, ty))

    t_surf = fonts["large"].render(offering.name, True, TEXT_WHITE)
    surface.blit(t_surf, (tx, ty + 18))

    # Buff
    b_lbl = fonts["med"].render(f"▲ БАФФ: {offering.buff_title}", True, TEXT_GREEN)
    surface.blit(b_lbl, (tx, ty + 44))
    b_desc = fonts["small"].render(offering.buff_desc, True, (200, 240, 215))
    surface.blit(b_desc, (tx, ty + 64))

    # Debuff
    d_lbl = fonts["med"].render(f"▼ ДЕБАФФ: {offering.debuff_title}", True, TEXT_RED)
    surface.blit(d_lbl, (tx, ty + 80))
    d_desc = fonts["small"].render(offering.debuff_desc, True, (240, 190, 190))
    surface.blit(d_desc, (tx, ty + 98))
