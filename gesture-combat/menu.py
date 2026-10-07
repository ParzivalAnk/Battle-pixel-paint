"""
menu.py - Authentic 16-Bit Pixel-Art Main Menu & Difficulty Selection UI for GLYPH-BLADE
Renders handcrafted pixel-art mini-drawings, retro beveled buttons, animated embers,
the interactive Difficulty Selection modal, and the Hardcore Challenges & Debuffs Altar.
"""

import math
import random
import pygame
from difficulty import DIFFICULTIES, DIFFICULTY_ORDER, DIFFICULTY_MANAGER
from challenges import CHALLENGES, CHALLENGE_ORDER, CHALLENGE_MANAGER

# =============================================================================
# 16-BIT RETRO COLOR PALETTE FOR PIXEL-ART ICONS
# =============================================================================
PALETTE = {
    ".": (0, 0, 0, 0),         # Transparent
    "K": (10, 12, 18, 255),     # Dark Outline (Black/Dark Slate)
    "k": (25, 30, 42, 255),     # Muted Outline
    "W": (255, 255, 255, 255), # Pure White Highlight
    "S": (180, 200, 220, 255), # Silver / Bright Steel
    "s": (110, 130, 155, 255), # Dark Steel / Shadow
    "G": (255, 215, 60, 255),  # Pure Gold
    "g": (240, 175, 30, 255),  # Medium Gold
    "d": (160, 105, 15, 255),  # Bronze / Dark Gold Shadow
    "R": (255, 50, 60, 255),   # Crimson Red
    "r": (175, 20, 35, 255),   # Dark Blood Red
    "F": (255, 140, 30, 255),  # Fire Orange
    "Y": (255, 235, 90, 255),  # Flame Yellow
    "P": (220, 90, 255, 255),  # Bright Purple Arcane
    "p": (145, 45, 185, 255),  # Dark Purple Arcane
    "C": (100, 235, 255, 255), # Bright Cyan Mana
    "c": (40, 155, 205, 255),  # Dark Cyan Mana
    "E": (100, 240, 120, 255), # Emerald Green
    "e": (40, 160, 60, 255),   # Dark Forest Green
    "B": (175, 115, 60, 255),  # Wood / Leather Brown
    "b": (115, 70, 30, 255),   # Dark Wood Shadow
    "T": (230, 190, 140, 255), # Straw / Rope / Light Wood
}

# =============================================================================
# 20x20 PIXEL-ART MINI-DRAWINGS FOR MENU BUTTONS
# =============================================================================

# 1. SWORD (START / «В БОЙ»): Diagonal Flaming Runic Blade
ICON_SWORD = [
    "..................YF",
    "...............YFFFK",
    "............YFFFSSWK",
    ".........YFFFSSSSWK.",
    "......YFFFSSSSSsWK..",
    "...YFFFSSSSSsWKk....",
    "...RFFSSSSSsWKk.....",
    "..RRFFSSSsWKk.F.....",
    "..rRFSSSsWKk..FF....",
    "...rRFsWKk....FFF...",
    "....rKdKk......FF...",
    "....KgGgK...........",
    "...KgGGggK..........",
    "...dGd.dGdK.........",
    "....K...KgK.........",
    ".........KBBK.......",
    "..........KBBK......",
    "...........KgK......",
    "..........KgRGK.....",
    "...........KKK......"
]

# 2. SKULL (DIFFICULTY / «УРОВЕНЬ СЛОЖНОСТИ»): Horned Demon Skull with Burning Cyan Eyes
ICON_SKULL = [
    ".rr.............rr..",
    "kRRk...........kRRk.",
    "kRRRk.........kRRRk.",
    ".kRRRk.......kRRRk..",
    "..kRRRkKKKKKkRRRk...",
    "...kRkWWWWWWWkRk....",
    "....kWSWWWWWSWk.....",
    "...kWSWSSsSSWSWk....",
    "...kSSSSSSSSSSSk....",
    "..kSSSsKKsKKsSSSk...",
    "..kSSsKCkSKCkSSSk...",
    "..kSSsKCkSKCkSSSk...",
    "..kSSSsKksKksSSSk...",
    "...kSSSsssssSSSk....",
    "....kSSsSsSsSSk.....",
    "....kKsKsKsKsKk.....",
    "....kSWsWsWsWSk.....",
    ".....kWWsWsWWk......",
    "......kKKKKKk.......",
    "...................."
]

# 3. TROPHY (ACHIEVEMENTS / «ЗАЛ СЛАВЫ & ДОСТИЖЕНИЯ»): Golden Chalice with Ruby Gem & Star
ICON_TROPHY = [
    ".........Y..........",
    "........YW..........",
    ".......YYWYY........",
    "........YW..........",
    ".........Y..........",
    "...KKKKKKKKKKKKK....",
    "..KGgGGGGGGGGGgGK...",
    ".KgKGGGGGGGGGGKgK...",
    ".KgKGGGrRRrGGGKgK...",
    ".KdKdGGrRRrGGdKdK...",
    "..KdKKGGWWGGKKdK....",
    "...KKdGGGGGGdKK.....",
    ".....KdGGGGdK.......",
    "......KdGGdK........",
    ".......KdKK.........",
    ".......KGdK.........",
    "......KgGgdK........",
    "....KKGGGGGGKK......",
    "...KgGGGGGGGGgK.....",
    "...KKKKKKKKKKKK....."
]

# 4. DOJO (DOJO / «ТРЕНИРОВОЧНОЕ ДОДЗЁ»): Training Dummy with Headband & Crossed Bokkens
ICON_DOJO = [
    "....bb........bb....",
    ".....bBB....BBb.....",
    "......bBB..BBb......",
    ".......bBBBBb.......",
    ".....KKKKKKKKKK.....",
    "....KTTTTTTTTTTK....",
    "...KTRRRRRRRRRRTK...",
    "...KTTRRTTTRRRTKK...",
    "...KTTTTTTTTTTTK....",
    "...KTkTTTTTTkTTK....",
    "....KTTTssTTTTK.....",
    "....KKTTTTTTKK......",
    "...KBKKKKKKKKKBK....",
    "..KBBKTTTTTTKBBK....",
    ".KBBKTTRRRTTKBBK....",
    "....KTTRRRTTK.......",
    "....KTTTTTTTK.......",
    "....KBBBBBBBK.......",
    "....KBBBBBBBK.......",
    "....KKKKKKKKK......."
]

# 5. GLYPH FORGE (CUSTOM GLYPH / «КУЗНИЦА СВОИХ ЗНАКОВ»): Arcane Quill Drawing a Glowing Rune
ICON_FORGE = [
    "..................Pp",
    "................PPp.",
    "...............PWPp.",
    "..............PWPp..",
    ".............PWCPp..",
    "............PWCCPp..",
    "...........PWCCPp...",
    "..........PWCcpp....",
    ".........PWccpp.....",
    "........PWccpp......",
    ".......PWccpp.......",
    "......PWccpp........",
    ".....KGCKp..........",
    "....KGgCKk..........",
    "...KdGKKp........P..",
    "...KK...Cp......PWP.",
    ".........Cp...CPWCP.",
    "..........CP..CWWCP.",
    "...........CPP.PWP..",
    "............CC...P.."
]

# 6. QUIT (QUIT / «ВЫХОД ИЗ ИГРЫ»): Iron Dungeon Gate & Flaming Torch
ICON_QUIT = [
    "....KKKKKKKKKK......",
    "...KssSSSSssK.......",
    "..KsSKssssKSsK..Y...",
    ".KsSK.KsSK.KsSK.FY..",
    ".KsK..KsK..KsK.RFF..",
    "KsSK..KsK..KsSK.rR..",
    "KsSK..KsK..KsSK.bK..",
    "KsSK..KsK..KsSK.bK..",
    "KsSK.KKgGKKKsSK.KK..",
    "KsSK.KgGGGgKsSK.....",
    "KsSK.KgGGGgKsSK.....",
    "KsSK.KKGdGKKKsSK....",
    "KsSK..KsK..KsSK.....",
    "KsSK..KsK..KsSK.....",
    "KsSK..KsK..KsSK.....",
    "KsSK..KsK..KsSK.....",
    "KsSK..KsK..KsSK.....",
    ".KsK..KsK..KsK......",
    ".KsSK.KsSK.KsSK.....",
    "..KKKKKKKKKKKK......"
]

# 7. BACK (NAVIGATION / «НАЗАД В МЕНЮ»): Silver Pixel Arrow Shield
ICON_BACK = [
    "....................",
    "....................",
    ".........KK.........",
    "........KsSK........",
    ".......KsSSK........",
    "......KsSSSK........",
    ".....KsSSSSKKKKKK...",
    "....KsSSSSSSSSSSK...",
    "...KsSSSSSSSSSSSK...",
    "..KsSSKKKKKKKKKKK...",
    "..KsSSKKKKKKKKKKK...",
    "...KsSSSSSSSSSSSK...",
    "....KsSSSSSSSSSSK...",
    ".....KsSSSSKKKKKK...",
    "......KsSSSK........",
    ".......KsSSK........",
    "........KsSK........",
    ".........KK.........",
    "....................",
    "...................."
]

def render_ascii_icon(grid, palette, scale=2):
    """Converts a 20x20 ASCII matrix into a crisp, scaled pygame Surface."""
    h = len(grid)
    w = max(len(row) for row in grid)
    base_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            col = palette.get(char, (0, 0, 0, 0))
            if col[3] > 0:
                base_surf.set_at((x, y), col)
    if scale > 1:
        return pygame.transform.scale(base_surf, (w * scale, h * scale))
    return base_surf

# Cached rendered icon surfaces (40x40 px)
PIXEL_ICONS_CACHE = {}

def get_pixel_icon(icon_id):
    """Retrieves or creates a pre-rendered 40x40 pixel icon surface."""
    global PIXEL_ICONS_CACHE
    if not PIXEL_ICONS_CACHE:
        PIXEL_ICONS_CACHE["SWORD"] = render_ascii_icon(ICON_SWORD, PALETTE, scale=2)
        PIXEL_ICONS_CACHE["SKULL"] = render_ascii_icon(ICON_SKULL, PALETTE, scale=2)
        PIXEL_ICONS_CACHE["TROPHY"] = render_ascii_icon(ICON_TROPHY, PALETTE, scale=2)
        PIXEL_ICONS_CACHE["DOJO"] = render_ascii_icon(ICON_DOJO, PALETTE, scale=2)
        PIXEL_ICONS_CACHE["FORGE"] = render_ascii_icon(ICON_FORGE, PALETTE, scale=2)
        PIXEL_ICONS_CACHE["QUIT"] = render_ascii_icon(ICON_QUIT, PALETTE, scale=2)
        PIXEL_ICONS_CACHE["BACK"] = render_ascii_icon(ICON_BACK, PALETTE, scale=2)
    return PIXEL_ICONS_CACHE.get(icon_id)


# =============================================================================
# REUSABLE 16-BIT PIXEL-ART BUTTON RENDERER
# =============================================================================
def draw_pixel_button(surface, rect, label, subtext="", key_badge="", icon_surface=None, theme_color=(255, 215, 80), is_hover=False, fonts=None, anim_time=0.0, show_chevron=None):
    """
    Renders an authentic 16-bit pixel-art button:
    - Chamfered/notched 2px pixel corners
    - 3D beveled pixel highlight & deep shadow
    - Forged pixel corner rivets
    - Dedicated equipment slot icon box with ambient illumination
    - Shortcut key badge and dual-line typography
    - Interactive animated chevron (►)
    """
    if show_chevron is None:
        show_chevron = bool(subtext)

    # 1. Base Fill & Notched Corners
    base_col = (30, 40, 60) if is_hover else (14, 18, 28)
    pygame.draw.rect(surface, base_col, rect)

    # Outer 2px dark border with stepped 2px corner cutouts
    outer_col = (8, 10, 16)
    pygame.draw.line(surface, outer_col, (rect.x + 3, rect.y), (rect.right - 4, rect.y), 2)
    pygame.draw.line(surface, outer_col, (rect.x + 3, rect.bottom - 1), (rect.right - 4, rect.bottom - 1), 2)
    pygame.draw.line(surface, outer_col, (rect.x, rect.y + 3), (rect.x, rect.bottom - 4), 2)
    pygame.draw.line(surface, outer_col, (rect.right - 1, rect.y + 3), (rect.right - 1, rect.bottom - 4), 2)

    # 2. Beveled 3D Pixel Rim
    if is_hover:
        pulse = 0.5 + 0.5 * math.sin(anim_time * 6.0)
        hi_col = (
            int(theme_color[0] * (0.85 + 0.15 * pulse)),
            int(theme_color[1] * (0.85 + 0.15 * pulse)),
            int(theme_color[2] * (0.85 + 0.15 * pulse))
        )
        sh_col = (max(12, int(theme_color[0] * 0.4)), max(12, int(theme_color[1] * 0.4)), max(12, int(theme_color[2] * 0.4)))
    else:
        hi_col = (70, 92, 130)
        sh_col = (10, 14, 22)

    # Top & Left highlight (2px)
    pygame.draw.line(surface, hi_col, (rect.x + 2, rect.y + 2), (rect.right - 3, rect.y + 2), 2)
    pygame.draw.line(surface, hi_col, (rect.x + 2, rect.y + 2), (rect.x + 2, rect.bottom - 3), 2)
    # Bottom & Right shadow (2px)
    pygame.draw.line(surface, sh_col, (rect.x + 3, rect.bottom - 3), (rect.right - 3, rect.bottom - 3), 2)
    pygame.draw.line(surface, sh_col, (rect.right - 3, rect.y + 3), (rect.right - 3, rect.bottom - 3), 2)

    # 3. Metallic Corner Studs / Rivets (4x4 pixels)
    rivet_hi = (255, 235, 140) if is_hover else (145, 165, 195)
    rivet_sh = (130, 95, 30) if is_hover else (22, 28, 42)
    for (rx, ry) in [(rect.x + 5, rect.y + 5), (rect.right - 9, rect.y + 5),
                     (rect.x + 5, rect.bottom - 9), (rect.right - 9, rect.bottom - 9)]:
        pygame.draw.rect(surface, (10, 12, 18), (rx - 1, ry - 1, 5, 5))
        pygame.draw.rect(surface, rivet_hi, (rx, ry, 2, 2))
        pygame.draw.rect(surface, rivet_sh, (rx + 1, ry + 1, 2, 2))

    # 4. Layout
    if subtext:
        # Standard Menu Button Layout (Left-aligned with subtext)
        content_offset_x = rect.x + 16
        if icon_surface:
            ibox_w, ibox_h = 46, 46
            ibox = pygame.Rect(rect.x + 10, rect.centery - ibox_h // 2, ibox_w, ibox_h)
            ibox_bg = (18, 24, 38) if not is_hover else (36, 48, 72)
            pygame.draw.rect(surface, ibox_bg, ibox)
            pygame.draw.rect(surface, (8, 10, 16), ibox, 1)

            pygame.draw.line(surface, (10, 14, 20), (ibox.x, ibox.y), (ibox.right, ibox.y), 1)
            pygame.draw.line(surface, (10, 14, 20), (ibox.x, ibox.y), (ibox.x, ibox.bottom), 1)
            pygame.draw.line(surface, (60, 80, 115) if not is_hover else hi_col, (ibox.x, ibox.bottom - 1), (ibox.right, ibox.bottom - 1), 1)
            pygame.draw.line(surface, (60, 80, 115) if not is_hover else hi_col, (ibox.right - 1, ibox.y), (ibox.right - 1, ibox.bottom), 1)

            if is_hover:
                glow_surf = pygame.Surface((38, 38), pygame.SRCALPHA)
                glow_col = (theme_color[0], theme_color[1], theme_color[2], 55)
                pygame.draw.circle(glow_surf, glow_col, (19, 19), 18)
                surface.blit(glow_surf, (ibox.centerx - 19, ibox.centery - 19))

            surface.blit(icon_surface, (ibox.centerx - icon_surface.get_width() // 2, ibox.centery - icon_surface.get_height() // 2))
            content_offset_x = ibox.right + 12

        if key_badge and fonts:
            badge_w, badge_h = 34, 22
            badge_rect = pygame.Rect(content_offset_x, rect.y + 11, badge_w, badge_h)
            badge_bg = (22, 30, 46) if not is_hover else (42, 54, 82)
            pygame.draw.rect(surface, badge_bg, badge_rect)
            pygame.draw.rect(surface, theme_color if is_hover else (80, 100, 140), badge_rect, 1)
            k_s = fonts["small"].render(key_badge, True, theme_color if is_hover else (180, 200, 230))
            surface.blit(k_s, (badge_rect.centerx - k_s.get_width() // 2, badge_rect.centery - k_s.get_height() // 2))
            content_offset_x = badge_rect.right + 10

        if fonts:
            t_col = (255, 255, 255) if is_hover else (215, 230, 245)
            t_font = fonts.get("large", fonts.get("med"))
            t_s = t_font.render(label, True, t_col)
            surface.blit(t_s, (content_offset_x, rect.y + 9))

            sub_col = theme_color if is_hover else (140, 160, 190)
            sub_s = fonts["small"].render(subtext, True, sub_col)
            surface.blit(sub_s, (content_offset_x, rect.y + 33))

    else:
        # Centered Modal / Navigation Button Layout
        tot_w = 0
        t_font = fonts.get("large", fonts.get("med")) if fonts else None
        t_s = t_font.render(label, True, (255, 255, 255) if is_hover else (215, 230, 245)) if t_font else None

        if icon_surface:
            tot_w += 44
        if key_badge and fonts:
            tot_w += (10 if tot_w > 0 else 0) + 38
        if t_s:
            tot_w += (10 if tot_w > 0 else 0) + t_s.get_width()

        cur_x = rect.centerx - tot_w // 2

        if icon_surface:
            ibox_w, ibox_h = 40, 40
            ibox = pygame.Rect(cur_x, rect.centery - ibox_h // 2, ibox_w, ibox_h)
            ibox_bg = (18, 24, 38) if not is_hover else (36, 48, 72)
            pygame.draw.rect(surface, ibox_bg, ibox)
            pygame.draw.rect(surface, (8, 10, 16), ibox, 1)

            if is_hover:
                glow_surf = pygame.Surface((34, 34), pygame.SRCALPHA)
                glow_col = (theme_color[0], theme_color[1], theme_color[2], 55)
                pygame.draw.circle(glow_surf, glow_col, (17, 17), 16)
                surface.blit(glow_surf, (ibox.centerx - 17, ibox.centery - 17))

            surface.blit(icon_surface, (ibox.centerx - icon_surface.get_width() // 2, ibox.centery - icon_surface.get_height() // 2))
            cur_x += ibox_w + 10

        if key_badge and fonts:
            badge_w, badge_h = 36, 22
            badge_rect = pygame.Rect(cur_x, rect.centery - badge_h // 2, badge_w, badge_h)
            badge_bg = (22, 30, 46) if not is_hover else (42, 54, 82)
            pygame.draw.rect(surface, badge_bg, badge_rect)
            pygame.draw.rect(surface, theme_color if is_hover else (80, 100, 140), badge_rect, 1)
            k_s = fonts["small"].render(key_badge, True, theme_color if is_hover else (180, 200, 230))
            surface.blit(k_s, (badge_rect.centerx - k_s.get_width() // 2, badge_rect.centery - k_s.get_height() // 2))
            cur_x += badge_w + 10

        if t_s:
            surface.blit(t_s, (cur_x, rect.centery - t_s.get_height() // 2))

    # 5. Right Decorative Chevron (►) if enabled
    if show_chevron and fonts:
        chv_col = theme_color if is_hover else (70, 90, 125)
        sym_font = fonts.get("sym_med", fonts.get("large"))
        chv_s = sym_font.render("►", True, chv_col)
        chv_x = rect.right - 28 + (int(3 * math.sin(anim_time * 8.0)) if is_hover else 0)
        surface.blit(chv_s, (chv_x, rect.centery - chv_s.get_height() // 2))


# =============================================================================
# PROCEDURAL EMBER PARTICLES FOR MENU
# =============================================================================
MENU_EMBERS = []

def init_menu_embers(count=35, width=1280, height=720):
    global MENU_EMBERS
    MENU_EMBERS = []
    for _ in range(count):
        MENU_EMBERS.append({
            "x": random.uniform(0, width),
            "y": random.uniform(0, height),
            "speed_y": random.uniform(18.0, 45.0),
            "speed_x": random.uniform(-15.0, 15.0),
            "radius": random.uniform(1.5, 3.5),
            "alpha": random.uniform(120, 240),
            "color": random.choice([
                (255, 90, 70),   # crimson ember
                (210, 100, 255), # violet arcane spark
                (255, 200, 80),  # golden rune flake
                (140, 220, 255)  # cyan wisp
            ])
        })

def update_menu_embers(dt, width=1280, height=720):
    for p in MENU_EMBERS:
        p["y"] -= p["speed_y"] * dt
        p["x"] += p["speed_x"] * dt
        if p["y"] < -10:
            p["y"] = height + random.uniform(5, 20)
            p["x"] = random.uniform(0, width)


# =============================================================================
# MAIN MENU SCREEN RENDERER
# =============================================================================
def draw_main_menu(surface, anim_time, fonts, bg_image=None, mouse_pos=None):
    """
    Renders the retro pixel-art main menu screen with custom handcrafted button drawings
    and active challenge modifiers badge.
    """
    w, h = surface.get_width(), surface.get_height()

    if not MENU_EMBERS:
        init_menu_embers(35, w, h)

    # 1. Background image or fallback dark fill
    if bg_image:
        surface.blit(bg_image, (0, 0))
        # Atmospheric dark overlay for readability
        dark_ov = pygame.Surface((w, h), pygame.SRCALPHA)
        dark_ov.fill((6, 8, 14, 150))
        surface.blit(dark_ov, (0, 0))
    else:
        surface.fill((10, 13, 20))

    # 2. Floating embers
    for p in MENU_EMBERS:
        surf_dot = pygame.Surface((int(p["radius"] * 2 + 2), int(p["radius"] * 2 + 2)), pygame.SRCALPHA)
        c = p["color"]
        pygame.draw.circle(surf_dot, (c[0], c[1], c[2], int(p["alpha"])), (int(p["radius"] + 1), int(p["radius"] + 1)), int(p["radius"]))
        surface.blit(surf_dot, (int(p["x"]), int(p["y"])))

    # 3. Title Glow & Text
    pulse = 0.5 + 0.5 * math.sin(anim_time * 2.8)
    title_col = (255, int(210 + 35 * pulse), int(70 + 30 * pulse))

    # Glow shadow
    shadow_surf = fonts["title"].render("GLYPH-BLADE", True, (140, 40, 200))
    surface.blit(shadow_surf, (w // 2 - shadow_surf.get_width() // 2 + 3, 50 + 3))

    title_surf = fonts["title"].render("GLYPH-BLADE", True, title_col)
    surface.blit(title_surf, (w // 2 - title_surf.get_width() // 2, 50))

    sub_surf = fonts["med"].render("DARK FANTASY ROGUELIKE • СИНТЕЗ ГЛИФОВ И 204 КОМБО", True, (180, 205, 235))
    surface.blit(sub_surf, (w // 2 - sub_surf.get_width() // 2, 108))

    # 4. Current Difficulty Indicator Banner + Challenges Count
    diff = DIFFICULTY_MANAGER.current
    ch_count = CHALLENGE_MANAGER.get_active_count()
    ch_badge = CHALLENGE_MANAGER.get_badge_text()

    banner_w = 600 if ch_count > 0 else 540
    diff_banner = pygame.Rect(w // 2 - banner_w // 2, 146, banner_w, 36)
    pygame.draw.rect(surface, (14, 18, 28, 220), diff_banner, border_radius=6)
    banner_bdr = (255, 90, 200) if ch_count > 0 else diff.color
    pygame.draw.rect(surface, banner_bdr, diff_banner, 1, border_radius=6)

    lbl_d1 = fonts["small"].render("СЛОЖНОСТЬ:", True, (180, 190, 210))
    sym_icon = fonts["sym_med"].render(diff.icon, True, diff.color)
    d_text = f"{diff.badge} — {diff.name}" + (f"  {ch_badge}" if ch_count > 0 else "")
    lbl_d2 = fonts["med"].render(d_text, True, (255, 120, 220) if ch_count > 0 else diff.color)

    total_dw = lbl_d1.get_width() + sym_icon.get_width() + lbl_d2.get_width() + 14
    cur_x = diff_banner.centerx - total_dw // 2
    surface.blit(lbl_d1, (cur_x, diff_banner.centery - lbl_d1.get_height() // 2))
    cur_x += lbl_d1.get_width() + 6
    surface.blit(sym_icon, (cur_x, diff_banner.centery - sym_icon.get_height() // 2))
    cur_x += sym_icon.get_width() + 6
    surface.blit(lbl_d2, (cur_x, diff_banner.centery - lbl_d2.get_height() // 2))

    # 5. Interactive Pixel-Art Menu Buttons with Mini-Drawings
    chal_sub = f"4 ранга • {ch_count} усложнений активно (Только дебаффы, 0 баффов)" if ch_count > 0 else "4 ранга • 7 усложнений (Только дебаффы, 0 баффов)"
    buttons = [
        {
            "id": "START",
            "key": "[1]",
            "label": "В БОЙ / НАЧАТЬ ЗАБЕГ",
            "sub": "Погружение в чертоги Бездны и битвы с боссами",
            "color": (255, 215, 80),
            "icon": "SWORD"
        },
        {
            "id": "DIFFICULTY",
            "key": "[2]",
            "label": "СЛОЖНОСТЬ & ЧЕЛЛЕНДЖИ",
            "sub": chal_sub,
            "color": (120, 230, 255) if ch_count == 0 else (255, 110, 220),
            "icon": "SKULL"
        },
        {
            "id": "ACHIEVEMENTS",
            "key": "[3]",
            "label": "ЗАЛ СЛАВЫ & ДОСТИЖЕНИЯ",
            "sub": "15 наград, секретные испытания и трофеи",
            "color": (255, 185, 60),
            "icon": "TROPHY"
        },
        {
            "id": "DOJO",
            "key": "[4]",
            "label": "ТРЕНИРОВОЧНОЕ ДОДЗЁ",
            "sub": "Отработка комбо на бессмертных манекенах",
            "color": (140, 245, 140),
            "icon": "DOJO"
        },
        {
            "id": "CUSTOM_GLYPH",
            "key": "[5]",
            "label": "КУЗНИЦА СВОИХ ЗНАКОВ [K]",
            "sub": "Нарисуй и сохрани собственный символ клинка",
            "color": (235, 130, 255),
            "icon": "FORGE"
        },
        {
            "id": "QUIT",
            "key": "[6]",
            "label": "ВЫХОД ИЗ ИГРЫ",
            "sub": "Покинуть темные чертоги подземелья",
            "color": (240, 75, 75),
            "icon": "QUIT"
        }
    ]

    btn_w = 560
    btn_h = 58
    start_y = 202
    gap = 68
    m_pos = mouse_pos if mouse_pos is not None else pygame.mouse.get_pos()
    rect_dict = {}

    for idx, b in enumerate(buttons):
        by = start_y + idx * gap
        b_rect = pygame.Rect(w // 2 - btn_w // 2, by, btn_w, btn_h)
        is_hov = b_rect.collidepoint(m_pos)
        rect_dict[b["id"]] = b_rect

        icon_surf = get_pixel_icon(b["icon"])
        draw_pixel_button(
            surface, b_rect,
            label=b["label"],
            subtext=b["sub"],
            key_badge=b["key"],
            icon_surface=icon_surf,
            theme_color=b["color"],
            is_hover=is_hov,
            fonts=fonts,
            anim_time=anim_time
        )

    # Version / footer
    ftr_surf = fonts["small"].render("GLYPH-BLADE v2.4 • Управление: Клавиши 1-6 или Мышь", True, (130, 150, 180))
    surface.blit(ftr_surf, (w // 2 - ftr_surf.get_width() // 2, h - 35))

    return rect_dict


def fit_text_width(text, font, max_w):
    if not text or font.size(text)[0] <= max_w:
        return text
    while len(text) > 4 and font.size(text + "...")[0] > max_w:
        text = text[:-1]
    return text + "..."


def draw_difficulty_modal(surface, anim_time, fonts, mouse_pos=None, current_tab=0):
    """
    Renders the full-screen difficulty selection screen with two tabs:
    Tab 0: Core Difficulty Ranks (Apprentice -> Nightmare)
    Tab 1: Hardcore Challenge Modifiers & Debuffs Altar (Only Debuffs, Instant Adaptation, etc.)
    """
    w, h = surface.get_width(), surface.get_height()
    m_pos = mouse_pos if mouse_pos is not None else pygame.mouse.get_pos()

    # Atmospheric dim overlay
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    ov.fill((8, 11, 18, 248))
    surface.blit(ov, (0, 0))

    # Top Tab Navigation Buttons
    tab_w = 320
    tab_h = 42
    tab_y = 35
    btn_tab_diff = pygame.Rect(w // 2 - tab_w - 12, tab_y, tab_w, tab_h)
    btn_tab_chal = pygame.Rect(w // 2 + 12, tab_y, tab_w, tab_h)

    hov_tab_d = btn_tab_diff.collidepoint(m_pos)
    hov_tab_c = btn_tab_chal.collidepoint(m_pos)

    # Render Tab 1 (Ranks)
    is_d_active = (current_tab == 0)
    pygame.draw.rect(surface, (28, 38, 58) if is_d_active else ((22, 28, 42) if hov_tab_d else (14, 18, 28)), btn_tab_diff, border_radius=6)
    pygame.draw.rect(surface, (255, 215, 80) if is_d_active else (60, 80, 110), btn_tab_diff, 2 if is_d_active else 1, border_radius=6)
    t_d_surf = fonts["med"].render("[Q] РАНГ СЛОЖНОСТИ", True, (255, 220, 80) if is_d_active else (180, 195, 215))
    surface.blit(t_d_surf, (btn_tab_diff.centerx - t_d_surf.get_width() // 2, btn_tab_diff.centery - t_d_surf.get_height() // 2))

    # Render Tab 2 (Challenges)
    is_c_active = (current_tab == 1)
    ch_count = CHALLENGE_MANAGER.get_active_count()
    chal_tab_title = f"[E] УСЛОЖНЕНИЯ & ЧЕЛЛЕНДЖИ ({ch_count} АКТИВНО)" if ch_count > 0 else "[E] УСЛОЖНЕНИЯ & ЧЕЛЛЕНДЖИ [TAB]"
    pygame.draw.rect(surface, (38, 22, 48) if is_c_active else ((26, 20, 36) if hov_tab_c else (14, 18, 28)), btn_tab_chal, border_radius=6)
    pygame.draw.rect(surface, (240, 90, 255) if is_c_active else ((210, 80, 230) if ch_count > 0 else (60, 80, 110)), btn_tab_chal, 2 if is_c_active else 1, border_radius=6)
    t_c_surf = fonts["med"].render(chal_tab_title, True, (255, 120, 255) if (is_c_active or ch_count > 0) else (180, 195, 215))
    surface.blit(t_c_surf, (btn_tab_chal.centerx - t_c_surf.get_width() // 2, btn_tab_chal.centery - t_c_surf.get_height() // 2))

    card_rects = {}
    btn_chal_banner = None
    challenge_rects = {}
    preset_rects = {}

    # =========================================================================
    # TAB 0: CORE DIFFICULTY RANKS
    # =========================================================================
    if current_tab == 0:
        sub_surf = fonts["large"].render("Выбери базовый ранг испытания для забега в глубины Бездны:", True, (190, 210, 235))
        surface.blit(sub_surf, (w // 2 - sub_surf.get_width() // 2, 92))

        # 4 Difficulty Cards
        card_w = 270
        card_h = 445
        gap = 22
        total_w = 4 * card_w + 3 * gap
        start_x = w // 2 - total_w // 2
        card_y = 132

        for idx, key in enumerate(DIFFICULTY_ORDER):
            diff = DIFFICULTIES[key]
            cx = start_x + idx * (card_w + gap)
            c_rect = pygame.Rect(cx, card_y, card_w, card_h)
            card_rects[key] = c_rect

            is_selected = (DIFFICULTY_MANAGER.current_key == key)
            is_hov = c_rect.collidepoint(m_pos)

            bg_col = (20, 28, 44) if is_selected else ((18, 24, 38) if is_hov else (12, 16, 26))
            bdr_col = diff.color if (is_selected or is_hov) else (50, 65, 90)
            bdr_width = 3 if is_selected else (2 if is_hov else 1)

            pygame.draw.rect(surface, bg_col, c_rect, border_radius=8)
            pygame.draw.rect(surface, bdr_col, c_rect, bdr_width, border_radius=8)

            if is_selected:
                sel_banner = pygame.Rect(c_rect.x + 8, c_rect.y + 8, c_rect.width - 16, 26)
                pygame.draw.rect(surface, diff.color, sel_banner, border_radius=4)
                sel_lbl = fonts["small"].render("ВЫБРАННАЯ СЛОЖНОСТЬ", True, (10, 15, 25))
                surface.blit(sel_lbl, (sel_banner.centerx - sel_lbl.get_width() // 2, sel_banner.centery - sel_lbl.get_height() // 2))

            ty = c_rect.y + 42
            sym_f = fonts.get("sym_large", fonts["large"])
            sym_s = sym_f.render(diff.icon, True, diff.color)
            badge_s = fonts["large"].render(diff.badge, True, diff.color)
            tot_bw = sym_s.get_width() + badge_s.get_width() + 8
            surface.blit(sym_s, (c_rect.centerx - tot_bw // 2, ty))
            surface.blit(badge_s, (c_rect.centerx - tot_bw // 2 + sym_s.get_width() + 8, ty))

            name_s = fonts["large"].render(diff.name.upper(), True, (255, 255, 255))
            surface.blit(name_s, (c_rect.centerx - name_s.get_width() // 2, ty + 28))

            # Description
            desc_box = pygame.Rect(c_rect.x + 12, ty + 64, c_rect.width - 24, 76)
            words = diff.desc.split()
            lines = []
            cur_line = ""
            for wd in words:
                test = cur_line + (" " if cur_line else "") + wd
                if len(test) < 26:
                    cur_line = test
                else:
                    lines.append(cur_line)
                    cur_line = wd
            if cur_line:
                lines.append(cur_line)

            ly = desc_box.y
            for l in lines[:4]:
                ls = fonts["small"].render(l, True, (190, 205, 225))
                surface.blit(ls, (c_rect.centerx - ls.get_width() // 2, ly))
                ly += 17

            # Stats
            stat_box = pygame.Rect(c_rect.x + 10, ty + 148, c_rect.width - 20, 178)
            pygame.draw.rect(surface, (15, 20, 32), stat_box, border_radius=6)
            pygame.draw.rect(surface, (40, 55, 80), stat_box, 1, border_radius=6)

            stats = [
                ("● HP Игрока:", f"{diff.player_hp}", (80, 255, 140) if diff.player_hp >= 100 else (255, 100, 100)),
                ("● Таймер этажа:", f"{int(diff.floor_timer)} сек.", (120, 220, 255) if diff.floor_timer >= 150 else (255, 140, 80)),
                ("● Урон врагов:", f"x{diff.enemy_damage_mult:.2f}", (255, 90, 90) if diff.enemy_damage_mult > 1.0 else (120, 240, 140)),
                ("● Скорость врагов:", f"x{diff.enemy_speed_mult:.2f}", (255, 120, 80) if diff.enemy_speed_mult > 1.0 else (160, 220, 255)),
                ("● Спам-порог:", f"{diff.spam_threshold_normal} / {diff.spam_threshold_boss} (босс)", (240, 140, 255)),
                ("● Шанс проклятий:", f"{int(diff.curse_chance * 100)}%", (210, 100, 255) if diff.curse_chance > 0.45 else (140, 200, 240))
            ]

            sy = stat_box.y + 7
            for k_s, v_s, val_col in stats:
                k_surf = fonts["small"].render(k_s, True, (170, 185, 205))
                v_surf = fonts["small"].render(v_s, True, val_col)
                surface.blit(k_surf, (stat_box.x + 8, sy))
                surface.blit(v_surf, (stat_box.right - v_surf.get_width() - 8, sy))
                sy += 27

            # Select button
            btn_sel = pygame.Rect(c_rect.x + 14, c_rect.bottom - 44, c_rect.width - 28, 34)
            b_col = diff.color if is_selected else ((35, 48, 70) if is_hov else (20, 28, 42))
            pygame.draw.rect(surface, b_col, btn_sel, border_radius=4)
            pygame.draw.rect(surface, diff.color, btn_sel, 1, border_radius=4)

            b_txt = "ВЫБРАНО" if is_selected else f"ВЫБРАТЬ [{idx + 1}]"
            txt_col = (10, 15, 25) if is_selected else (255, 255, 255)
            bt_surf = fonts["med"].render(b_txt, True, txt_col)
            surface.blit(bt_surf, (btn_sel.centerx - bt_surf.get_width() // 2, btn_sel.centery - bt_surf.get_height() // 2))

        # Challenges promo banner at bottom
        btn_chal_banner = pygame.Rect(w // 2 - 440, h - 128, 880, 42)
        hov_cb = btn_chal_banner.collidepoint(m_pos)
        pygame.draw.rect(surface, (28, 16, 38) if hov_cb else (16, 14, 26), btn_chal_banner, border_radius=6)
        pygame.draw.rect(surface, (240, 80, 255) if hov_cb else (160, 60, 190), btn_chal_banner, 2 if hov_cb else 1, border_radius=6)

        if ch_count > 0:
            cb_text = f"☠ АКТИВНЫЕ УСЛОЖНЕНИЯ: {ch_count} / 7 (ТОЛЬКО ДЕБАФФЫ, -6S ТАЙМЕР И ДР.) — НАЖМИ [TAB] ИЛИ КЛИКНИ ДЛЯ НАСТРОЙКИ ☠"
        else:
            cb_text = "☠ АЛТАРЬ УСЛОЖНЕНИЙ: ТОЛЬКО ДЕБАФФЫ (0 БАФФОВ), СТЕКЛЯННОЕ HP, АНТИ-СПАМ — НАЖМИ [TAB] ИЛИ КЛИКНИ ☠"

        cb_surf = fonts["med"].render(cb_text, True, (255, 140, 255) if hov_cb else (225, 110, 240))
        surface.blit(cb_surf, (btn_chal_banner.centerx - cb_surf.get_width() // 2, btn_chal_banner.centery - cb_surf.get_height() // 2))

    # =========================================================================
    # TAB 1: HARDCORE CHALLENGES & DEBUFFS ALTAR
    # =========================================================================
    else:
        sub_surf = fonts["large"].render("Алтарь Проклятий: Включай любые усложнения для настоящего хардкорного вызова:", True, (240, 160, 255))
        surface.blit(sub_surf, (w // 2 - sub_surf.get_width() // 2, 92))

        # Preset Quick Bar
        p_bar_y = 130
        presets = [
            ("only_curses", "[P] ПРЕСЕТ: ТОЛЬКО ДЕБАФФЫ [P]", (240, 80, 255)),
            ("titan_hell", "[H] ПРЕСЕТ: АД ТИТАНОВ [H]", (255, 90, 70)),
            ("glass_nightmare", "[G] СТЕКЛЯННЫЙ КОШМАР [G]", (255, 160, 50)),
            ("all", "[A] ВКЛЮЧИТЬ ВСЕ [A]", (255, 60, 60)),
            ("clear", "[C] ОЧИСТИТЬ ВСЕ [C]", (140, 160, 190))
        ]

        pb_w = 205
        pb_h = 32
        pb_gap = 14
        pb_start_x = w // 2 - (len(presets) * pb_w + (len(presets) - 1) * pb_gap) // 2

        for p_idx, (p_id, p_label, p_col) in enumerate(presets):
            p_rect = pygame.Rect(pb_start_x + p_idx * (pb_w + pb_gap), p_bar_y, pb_w, pb_h)
            preset_rects[p_id] = p_rect
            is_p_hov = p_rect.collidepoint(m_pos)

            pygame.draw.rect(surface, (28, 22, 38) if is_p_hov else (14, 16, 24), p_rect, border_radius=4)
            pygame.draw.rect(surface, p_col if is_p_hov else (70, 75, 95), p_rect, 1, border_radius=4)
            pl_surf = fonts["small"].render(p_label, True, p_col if is_p_hov else (200, 210, 225))
            surface.blit(pl_surf, (p_rect.centerx - pl_surf.get_width() // 2, p_rect.centery - pl_surf.get_height() // 2))

        # 7 Challenge Cards Grid
        # 6 cards in 2 columns + 7th card spanning both columns
        col_w = 525
        col_h = 92
        c_gap_x = 30
        c_gap_y = 14
        c_start_x = w // 2 - (col_w * 2 + c_gap_x) // 2
        c_start_y = 176

        for idx, ch_key in enumerate(CHALLENGE_ORDER):
            ch = CHALLENGES[ch_key]
            is_active = CHALLENGE_MANAGER.is_active(ch_key)

            if idx < 6:
                col = idx % 2
                row = idx // 2
                rect = pygame.Rect(c_start_x + col * (col_w + c_gap_x), c_start_y + row * (col_h + c_gap_y), col_w, col_h)
            else:
                # 7th card spans bottom width
                rect = pygame.Rect(c_start_x, c_start_y + 3 * (col_h + c_gap_y), col_w * 2 + c_gap_x, col_h - 10)

            challenge_rects[ch_key] = rect
            is_hov = rect.collidepoint(m_pos)

            # Card background
            if is_active:
                bg_col = (34, 18, 44) if not is_hov else (48, 24, 62)
                bdr_col = ch.color
                bdr_w = 2
            else:
                bg_col = (14, 16, 24) if not is_hov else (22, 26, 38)
                bdr_col = (60, 75, 100) if not is_hov else (120, 150, 195)
                bdr_w = 1

            pygame.draw.rect(surface, bg_col, rect, border_radius=6)
            pygame.draw.rect(surface, bdr_col, rect, bdr_w, border_radius=6)

            # Left Hotkey & Icon box
            ibox = pygame.Rect(rect.x + 10, rect.centery - 24, 48, 48)
            pygame.draw.rect(surface, (20, 22, 34) if not is_active else (50, 24, 66), ibox, border_radius=4)
            pygame.draw.rect(surface, ch.color if is_active else (80, 95, 125), ibox, 1, border_radius=4)

            k_s = fonts["small"].render(ch.hotkey, True, ch.color if is_active else (160, 175, 200))
            sym_f = fonts.get("sym_med", fonts["med"])
            ic_s = sym_f.render(ch.icon, True, ch.color if is_active else (180, 195, 220))
            surface.blit(k_s, (ibox.centerx - k_s.get_width() // 2, ibox.y + 5))
            surface.blit(ic_s, (ibox.centerx - ic_s.get_width() // 2, ibox.bottom - ic_s.get_height() - 4))

            # Header & Active Badge
            name_s = fonts["med"].render(ch.name, True, (255, 255, 255) if is_active else (210, 220, 235))
            surface.blit(name_s, (rect.x + 68, rect.y + 10))

            badge_text = "[ АКТИВНО: ВКЛ ]" if is_active else "[ ВЫКЛЮЧЕНО ]"
            badge_col = ch.color if is_active else (110, 125, 150)
            bdg_s = fonts["small"].render(badge_text, True, badge_col)
            surface.blit(bdg_s, (rect.right - bdg_s.get_width() - 14, rect.y + 11))

            # Description
            avail_w = rect.width - 82
            d_str = fit_text_width(ch.desc, fonts["small"], avail_w)
            d_s = fonts["small"].render(d_str, True, (215, 225, 240) if is_active else (160, 175, 195))
            surface.blit(d_s, (rect.x + 68, rect.y + 36))

            # Penalty
            p_str = fit_text_width(f"Штраф: {ch.penalty_desc}", fonts["small"], avail_w)
            p_s = fonts["small"].render(p_str, True, (255, 130, 120) if is_active else (140, 150, 170))
            surface.blit(p_s, (rect.x + 68, rect.y + 58))

    # Bottom Back Button with Pixel Button Styling & Back Arrow Icon
    btn_back = pygame.Rect(w // 2 - 170, h - 68, 340, 48)
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

    return {
        "current_tab": current_tab,
        "btn_tab_diff": btn_tab_diff,
        "btn_tab_chal": btn_tab_chal,
        "card_rects": card_rects,
        "btn_chal_banner": btn_chal_banner,
        "challenge_rects": challenge_rects,
        "preset_rects": preset_rects,
        "btn_back": btn_back
    }
