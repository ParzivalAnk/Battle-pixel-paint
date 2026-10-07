"""
achievements.py - Achievements System & UI for GLYPH-BLADE
Manages achievement registry, unlock triggers, json persistence,
real-time toast popups, and the full interactive Achievements Menu.
"""

import os
import json
import time
import math
import pygame

ACHIEVEMENTS_FILE = os.path.join(os.path.dirname(__file__), "achievements.json")

class Achievement:
    def __init__(self, id_key, title, desc, icon="★", tier="Обычное", tier_color=(200, 220, 240)):
        self.id = id_key
        self.title = title
        self.desc = desc
        self.icon = icon
        self.tier = tier
        self.tier_color = tier_color
        self.unlocked = False
        self.unlocked_at = None

    def to_dict(self):
        return {
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at
        }

    def from_dict(self, data):
        self.unlocked = data.get("unlocked", False)
        self.unlocked_at = data.get("unlocked_at", None)

DEFAULT_ACHIEVEMENTS = [
    Achievement(
        id_key="first_glyph",
        title="Первый Росчерк",
        desc="Начерти свой первый боевой глиф во время сражения на арене.",
        icon="⚔",
        tier="Обычное",
        tier_color=(170, 200, 230)
    ),
    Achievement(
        id_key="first_fusion",
        title="Мастер Синтеза",
        desc="Активируй первое составное комбо (напр. Крио-Метеорит или Разрыв).",
        icon="✦",
        tier="Редкое",
        tier_color=(120, 220, 255)
    ),
    Achievement(
        id_key="custom_glyph_creator",
        title="Творец Знаков",
        desc="Нарисуй и запечатай собственный символ в Кузнице Знаков [K].",
        icon="❂",
        tier="Редкое",
        tier_color=(255, 215, 80)
    ),
    Achievement(
        id_key="ultra_combo_cast",
        title="Полярный Катаклизм",
        desc="Синтезируй в Алтаре [C] и примени комбо из 3+ знаков через [F].",
        icon="❄",
        tier="Эпическое",
        tier_color=(140, 240, 255)
    ),
    Achievement(
        id_key="boss_slayer",
        title="Падение Колосса",
        desc="Одержи победу над первым великим Боссом подземелья.",
        icon="👑",
        tier="Эпическое",
        tier_color=(255, 200, 60)
    ),
    Achievement(
        id_key="curse_pact",
        title="Сделка с Бездной",
        desc="Прими Проклятый Дар Бездны (чистый дебафф) в портале этажа.",
        icon="☠",
        tier="Проклятое",
        tier_color=(220, 90, 255)
    ),
    Achievement(
        id_key="anti_spam_break",
        title="Пробивающий Барьер",
        desc="Пробей адаптировавшегося врага со щитом с помощью смены стихии.",
        icon="⚡",
        tier="Редкое",
        tier_color=(255, 240, 100)
    ),
    Achievement(
        id_key="slo_mo_parry",
        title="Владыка Времени",
        desc="Используй блок Бастиона [🛡] или Рокировку [⌛] для замедления времени.",
        icon="⌛",
        tier="Обычное",
        tier_color=(190, 160, 255)
    ),
    Achievement(
        id_key="floor_3_cleared",
        title="Глубины Тьмы",
        desc="Преодолей 3 этажа подземелья в рамках одного забега.",
        icon="★",
        tier="Эпическое",
        tier_color=(255, 170, 70)
    ),
    Achievement(
        id_key="flawless_wave",
        title="Неуязвимый Клинок",
        desc="Полностью зачисти волну врагов без получения урона.",
        icon="🛡",
        tier="Легендарное",
        tier_color=(255, 220, 100)
    ),
    Achievement(
        id_key="hardcore_victor",
        title="Триумф Инквизитора",
        desc="Зачисти этаж на сложности «Инквизитор» или «Кошмар Бездны».",
        icon="⚔",
        tier="Легендарное",
        tier_color=(255, 90, 90)
    ),
    Achievement(
        id_key="secret_archivist",
        title="Архивариус Рун",
        desc="Открой все 5 засекреченных стихий Бездны по мере прохождения.",
        icon="✦",
        tier="Легендарное",
        tier_color=(240, 120, 255)
    ),
    Achievement(
        id_key="liar_achievement",
        title="Врунишка",
        desc="Соврать боссу 50-го уровня, что ты прошел игру без получения урона.",
        icon="🎭",
        tier="Секретное",
        tier_color=(255, 110, 195)
    ),
    Achievement(
        id_key="cursed_survivor",
        title="Дитя Скверны",
        desc="Зачистить этаж с активным усложнением «Только дебаффы (ноль баффов)».",
        icon="☠",
        tier="Эпическое",
        tier_color=(230, 90, 255)
    ),
    Achievement(
        id_key="purgatory_conqueror",
        title="Покоритель Чистилища",
        desc="Одержать победу над Боссом с 3+ активными усложнениями Бездны.",
        icon="👑",
        tier="Легендарное",
        tier_color=(255, 60, 180)
    ),
    Achievement(
        id_key="divine_weapon_pickup",
        title="Сияние Первородных",
        desc="Подобрать оружие высшего ранга V, ослепительно сияющее белым светом.",
        icon="☀",
        tier="Легендарное",
        tier_color=(255, 255, 255)
    ),
    Achievement(
        id_key="arsenal_master",
        title="Оружейный Барон",
        desc="Собрать во всех 3 слотах редкое оружие ранга III и выше.",
        icon="⚔",
        tier="Эпическое",
        tier_color=(210, 100, 255)
    )
]

class AchievementManager:
    def __init__(self):
        self.achievements = {a.id: a for a in DEFAULT_ACHIEVEMENTS}
        self.popup_queue = []
        self.active_popup = None
        self.popup_timer = 0.0
        self.load()

    def load(self):
        if not os.path.exists(ACHIEVEMENTS_FILE):
            return
        try:
            with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for ach_id, item_data in data.items():
                    if ach_id in self.achievements:
                        self.achievements[ach_id].from_dict(item_data)
        except Exception as e:
            print(f"Error loading achievements: {e}")

    def save(self):
        try:
            data = {ach_id: a.to_dict() for ach_id, a in self.achievements.items()}
            with open(ACHIEVEMENTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving achievements: {e}")

    def unlock(self, ach_id, fx=None, sfx=None):
        if ach_id not in self.achievements:
            return False
        ach = self.achievements[ach_id]
        if ach.unlocked:
            return False

        ach.unlocked = True
        ach.unlocked_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.save()

        # Enqueue popup banner
        self.popup_queue.append(ach)
        if sfx:
            sfx.play("crit")
        if fx:
            fx.add_screen_shake(10.0)

        return True

    def get_progress(self):
        unlocked = sum(1 for a in self.achievements.values() if a.unlocked)
        total = len(self.achievements)
        pct = int((unlocked / total) * 100) if total > 0 else 0
        return unlocked, total, pct

    def update_popups(self, dt):
        if self.active_popup:
            self.popup_timer -= dt
            if self.popup_timer <= 0:
                self.active_popup = None
        elif self.popup_queue:
            self.active_popup = self.popup_queue.pop(0)
            self.popup_timer = 4.5

    def draw_active_popup(self, surface, anim_time, fonts):
        if not self.active_popup:
            return

        w, h = 480, 78
        cx = surface.get_width() // 2
        
        # Slide in animation
        t = 4.5 - self.popup_timer
        if t < 0.35:
            slide_progress = t / 0.35
            y = int(-h + (h + 20) * (1.0 - (1.0 - slide_progress)**2))
        elif self.popup_timer < 0.4:
            fade_progress = self.popup_timer / 0.4
            y = int(20 - (1.0 - fade_progress) * 100)
        else:
            y = 20

        rect = pygame.Rect(cx - w // 2, y, w, h)

        # Glow and border
        pulse = 0.5 + 0.5 * math.sin(anim_time * 8.0)
        border_col = (
            int(self.active_popup.tier_color[0] * (0.8 + 0.2 * pulse)),
            int(self.active_popup.tier_color[1] * (0.8 + 0.2 * pulse)),
            int(self.active_popup.tier_color[2] * (0.8 + 0.2 * pulse))
        )

        bg_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        bg_surf.fill((12, 16, 26, 240))
        surface.blit(bg_surf, (rect.x, rect.y))
        pygame.draw.rect(surface, border_col, rect, 2, border_radius=6)

        # Icon box
        ibox = pygame.Rect(rect.x + 12, rect.y + 12, 54, 54)
        pygame.draw.rect(surface, (20, 26, 42), ibox, border_radius=4)
        pygame.draw.rect(surface, self.active_popup.tier_color, ibox, 1, border_radius=4)
        
        sym_f = fonts.get("sym_large", fonts["large"])
        i_surf = sym_f.render(self.active_popup.icon, True, self.active_popup.tier_color)
        surface.blit(i_surf, (ibox.centerx - i_surf.get_width() // 2, ibox.centery - i_surf.get_height() // 2))

        # Title & Subtitle
        sym_sm = fonts.get("sym_small", fonts["small"])
        s_star = sym_sm.render("★", True, (255, 215, 80))
        head_s = fonts["small"].render(f"ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО! [{self.active_popup.tier}]", True, (255, 215, 80))
        surface.blit(s_star, (rect.x + 76, rect.y + 10))
        surface.blit(head_s, (rect.x + 76 + s_star.get_width() + 5, rect.y + 10))
        surface.blit(s_star, (rect.x + 76 + s_star.get_width() + 10 + head_s.get_width(), rect.y + 10))

        title_s = fonts["med"].render(self.active_popup.title, True, (255, 255, 255))
        surface.blit(title_s, (rect.x + 76, rect.y + 30))

        desc_s = fonts["small"].render(self.active_popup.desc[:50], True, (190, 205, 225))
        surface.blit(desc_s, (rect.x + 76, rect.y + 52))

ACHIEVEMENT_MANAGER = AchievementManager()

def draw_achievements_screen(surface, anim_time, fonts, scroll_page=0):
    """
    Renders the full interactive Achievements Menu.
    Supports pagination (6 achievements per page).
    """
    w, h = surface.get_width(), surface.get_height()

    # Dark atmospheric overlay
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    ov.fill((8, 12, 20, 248))
    surface.blit(ov, (0, 0))

    # Glowing title
    title_surf = fonts["title"].render("ЗАЛ СЛАВЫ И ДОСТИЖЕНИЙ", True, (255, 215, 80))
    surface.blit(title_surf, (w // 2 - title_surf.get_width() // 2, 40))

    # Progress bar and stats
    unlocked, total, pct = ACHIEVEMENT_MANAGER.get_progress()
    stat_text = f"Прогресс: {unlocked} из {total} разблокировано ({pct}%)"
    stat_surf = fonts["large"].render(stat_text, True, (180, 220, 255))
    surface.blit(stat_surf, (w // 2 - stat_surf.get_width() // 2, 92))

    # Progress bar graphic
    pb_w, pb_h = 460, 14
    pb_rect = pygame.Rect(w // 2 - pb_w // 2, 128, pb_w, pb_h)
    pygame.draw.rect(surface, (20, 28, 45), pb_rect, border_radius=4)
    fill_w = int(pb_w * (unlocked / max(1, total)))
    if fill_w > 0:
        pygame.draw.rect(surface, (255, 215, 80), (pb_rect.x, pb_rect.y, fill_w, pb_h), border_radius=4)
    pygame.draw.rect(surface, (70, 95, 140), pb_rect, 1, border_radius=4)

    # List of achievements (paginated: 6 items per page)
    items = list(ACHIEVEMENT_MANAGER.achievements.values())
    per_page = 6
    total_pages = max(1, math.ceil(len(items) / per_page))
    cur_page = max(0, min(scroll_page, total_pages - 1))
    page_items = items[cur_page * per_page : (cur_page + 1) * per_page]

    card_w = 780
    card_h = 76
    start_y = 160
    gap = 88
    cx = w // 2 - card_w // 2
    m_pos = pygame.mouse.get_pos()

    for idx, ach in enumerate(page_items):
        cy = start_y + idx * gap
        c_rect = pygame.Rect(cx, cy, card_w, card_h)
        is_hov = c_rect.collidepoint(m_pos)

        # Background
        if ach.unlocked:
            bg_col = (18, 25, 40) if not is_hov else (25, 36, 56)
            bdr_col = (100, 160, 230) if not is_hov else (255, 215, 80)
        else:
            bg_col = (12, 15, 22) if not is_hov else (16, 20, 30)
            bdr_col = (45, 55, 75)

        pygame.draw.rect(surface, bg_col, c_rect, border_radius=6)
        pygame.draw.rect(surface, bdr_col, c_rect, 2 if is_hov or ach.unlocked else 1, border_radius=6)

        # Icon box
        ibox = pygame.Rect(c_rect.x + 12, c_rect.y + 11, 54, 54)
        i_bg = (24, 32, 50) if ach.unlocked else (15, 18, 26)
        i_bdr = ach.tier_color if ach.unlocked else (60, 70, 90)
        pygame.draw.rect(surface, i_bg, ibox, border_radius=4)
        pygame.draw.rect(surface, i_bdr, ibox, 1, border_radius=4)

        sym_f = fonts.get("sym_large", fonts["large"])
        sym_col = ach.tier_color if ach.unlocked else (90, 100, 120)
        i_surf = sym_f.render(ach.icon if ach.unlocked else "🔒", True, sym_col)
        surface.blit(i_surf, (ibox.centerx - i_surf.get_width() // 2, ibox.centery - i_surf.get_height() // 2))

        # Title & Tier
        title_col = (255, 255, 255) if ach.unlocked else (140, 150, 170)
        t_text = ach.title if (ach.unlocked or ach.tier != "Секретное") else "??? Секретное Испытание ???"
        t_surf = fonts["med"].render(t_text, True, title_col)
        surface.blit(t_surf, (c_rect.x + 78, c_rect.y + 12))

        tier_surf = fonts["small"].render(f"[{ach.tier}]", True, ach.tier_color if ach.unlocked else (100, 110, 130))
        surface.blit(tier_surf, (c_rect.x + 84 + t_surf.get_width(), c_rect.y + 15))

        # Description
        desc_col = (190, 210, 235) if ach.unlocked else (110, 120, 140)
        d_text = ach.desc if (ach.unlocked or ach.tier != "Секретное") else "Условия разблокировки сокрыты в Чертоге Истины на 50-м этаже..."
        d_surf = fonts["small"].render(d_text, True, desc_col)
        surface.blit(d_surf, (c_rect.x + 78, c_rect.y + 40))

        # Status badge on right
        if ach.unlocked:
            status_text = "[ РАЗБЛОКИРОВАНО ]"
            status_col = (100, 255, 160)
        else:
            status_text = "[ ЗАБЛОКИРОВАНО ]"
            status_col = (120, 130, 150)

        s_surf = fonts["small"].render(status_text, True, status_col)
        surface.blit(s_surf, (c_rect.right - s_surf.get_width() - 18, c_rect.centery - s_surf.get_height() // 2))

    # Pagination and Back buttons
    if total_pages > 1:
        btn_prev = pygame.Rect(cx, h - 68, 160, 44)
        btn_back = pygame.Rect(w // 2 - 140, h - 68, 280, 44)
        btn_next = pygame.Rect(cx + card_w - 160, h - 68, 160, 44)
    else:
        btn_prev = pygame.Rect(-100, -100, 10, 10)
        btn_next = pygame.Rect(-100, -100, 10, 10)
        btn_back = pygame.Rect(w // 2 - 150, h - 68, 300, 44)

    page_lbl = fonts["med"].render(f"Страница {cur_page + 1} / {total_pages}", True, (200, 215, 240))
    surface.blit(page_lbl, (w // 2 - page_lbl.get_width() // 2, h - 110))

    from menu import draw_pixel_button, get_pixel_icon

    # Draw Back button with pixel styling
    hov_back = btn_back.collidepoint(m_pos)
    draw_pixel_button(
        surface, btn_back,
        label="НАЗАД В МЕНЮ [ESC]",
        subtext="",
        key_badge="ESC",
        icon_surface=get_pixel_icon("BACK"),
        theme_color=(255, 215, 80),
        is_hover=hov_back,
        fonts=fonts,
        anim_time=anim_time
    )

    # Prev / Next buttons
    if total_pages > 1:
        hov_prev = btn_prev.collidepoint(m_pos)
        draw_pixel_button(
            surface, btn_prev,
            label="◄ Предыдущая",
            subtext="",
            key_badge="",
            icon_surface=None,
            theme_color=(120, 200, 255),
            is_hover=hov_prev,
            fonts=fonts,
            anim_time=anim_time
        )

        hov_next = btn_next.collidepoint(m_pos)
        draw_pixel_button(
            surface, btn_next,
            label="Следующая ►",
            subtext="",
            key_badge="",
            icon_surface=None,
            theme_color=(120, 200, 255),
            is_hover=hov_next,
            fonts=fonts,
            anim_time=anim_time
        )

    return {
        "btn_back": btn_back,
        "btn_prev": btn_prev,
        "btn_next": btn_next,
        "cur_page": cur_page,
        "total_pages": total_pages
    }
