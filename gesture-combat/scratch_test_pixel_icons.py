"""
scratch_test_pixel_icons.py - Test generator for the 6 pixel art menu icons.
"""

import os
import math
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

# Shared Palette
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

# 20x20 pixel art definitions for the 6 menu buttons

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

# 3. TROPHY (ACHIEVEMENTS / «ЗАЛ ДОСТИЖЕНИЙ»): Ornate Golden Chalice with Gem & Star
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

# 5. GLYPH FORGE (CUSTOM GLYPH / «КУЗНИЦА ЗНАКОВ»): Arcane Quill & Glowing Rune
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

# 6. QUIT (QUIT / «ВЫХОД ИЗ ИГРЫ»): Iron Dungeon Gate & Torch
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

def render_ascii_icon(grid, palette, scale=2):
    """Converts a list of ASCII rows to a scaled, pixel-crisp pygame Surface."""
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

def draw_pixel_button(surface, rect, label, subtext, key_badge, icon_surface, theme_color, is_hover, fonts, anim_time=0.0):
    """Renders a fully authentic 16-bit pixel-art button with custom pixel drawing."""
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

    # 4. Pixel Icon Box (Left side of button)
    ibox_w, ibox_h = 46, 46
    ibox = pygame.Rect(rect.x + 12, rect.centery - ibox_h // 2, ibox_w, ibox_h)
    ibox_bg = (18, 24, 38) if not is_hover else (36, 48, 72)
    pygame.draw.rect(surface, ibox_bg, ibox)
    pygame.draw.rect(surface, (8, 10, 16), ibox, 1)

    # Inset frame
    pygame.draw.line(surface, (10, 14, 20), (ibox.x, ibox.y), (ibox.right, ibox.y), 1)
    pygame.draw.line(surface, (10, 14, 20), (ibox.x, ibox.y), (ibox.x, ibox.bottom), 1)
    pygame.draw.line(surface, (60, 80, 115) if not is_hover else hi_col, (ibox.x, ibox.bottom - 1), (ibox.right, ibox.bottom - 1), 1)
    pygame.draw.line(surface, (60, 80, 115) if not is_hover else hi_col, (ibox.right - 1, ibox.y), (ibox.right - 1, ibox.bottom), 1)

    # Soft ambient glow behind icon if hovered
    if is_hover:
        glow_surf = pygame.Surface((38, 38), pygame.SRCALPHA)
        glow_col = (theme_color[0], theme_color[1], theme_color[2], 55)
        pygame.draw.circle(glow_surf, glow_col, (19, 19), 18)
        surface.blit(glow_surf, (ibox.centerx - 19, ibox.centery - 19))

    # Blit the 40x40 pixel drawing!
    if icon_surface:
        surface.blit(icon_surface, (ibox.centerx - icon_surface.get_width() // 2, ibox.centery - icon_surface.get_height() // 2))

    # 5. Key Badge [1]
    badge_rect = pygame.Rect(rect.x + 66, rect.y + 12, 34, 22)
    badge_bg = (22, 30, 46) if not is_hover else (42, 54, 82)
    pygame.draw.rect(surface, badge_bg, badge_rect)
    pygame.draw.rect(surface, theme_color if is_hover else (80, 100, 140), badge_rect, 1)
    k_s = fonts["small"].render(key_badge, True, theme_color if is_hover else (180, 200, 230))
    surface.blit(k_s, (badge_rect.centerx - k_s.get_width() // 2, badge_rect.centery - k_s.get_height() // 2))

    # 6. Button Title & Subtext
    t_col = (255, 255, 255) if is_hover else (215, 230, 245)
    t_s = fonts["large"].render(label, True, t_col)
    surface.blit(t_s, (rect.x + 108, rect.y + 11))

    sub_col = theme_color if is_hover else (140, 160, 190)
    sub_s = fonts["small"].render(subtext, True, sub_col)
    surface.blit(sub_s, (rect.x + 108, rect.y + 35))

    # 7. Right Decorative Chevron (►)
    chv_col = theme_color if is_hover else (70, 90, 125)
    chv_s = fonts["large"].render("►", True, chv_col)
    chv_x = rect.right - 28 + (int(3 * math.sin(anim_time * 8.0)) if is_hover else 0)
    surface.blit(chv_s, (chv_x, rect.centery - chv_s.get_height() // 2))

def draw_pixel_button_preview():
    W, H = 1280, 720
    screen = pygame.Surface((W, H))
    screen.fill((10, 13, 20))

    fonts = {
        "large": pygame.font.SysFont("arial", 20, bold=True),
        "small": pygame.font.SysFont("arial", 13),
        "title": pygame.font.SysFont("arial", 32, bold=True)
    }

    icons = {
        "START": render_ascii_icon(ICON_SWORD, PALETTE, scale=2),
        "DIFFICULTY": render_ascii_icon(ICON_SKULL, PALETTE, scale=2),
        "ACHIEVEMENTS": render_ascii_icon(ICON_TROPHY, PALETTE, scale=2),
        "DOJO": render_ascii_icon(ICON_DOJO, PALETTE, scale=2),
        "CUSTOM_GLYPH": render_ascii_icon(ICON_FORGE, PALETTE, scale=2),
        "QUIT": render_ascii_icon(ICON_QUIT, PALETTE, scale=2),
    }

    buttons = [
        {"id": "START", "key": "[1]", "label": "В БОЙ / НАЧАТЬ ЗАБЕГ", "sub": "Погружение в бездну этажей и битвы с боссами", "color": (255, 215, 80)},
        {"id": "DIFFICULTY", "key": "[2]", "label": "УРОВЕНЬ СЛОЖНОСТИ", "sub": "4 режима: Ученик • Адепт • Инквизитор • Кошмар", "color": (120, 230, 255)},
        {"id": "ACHIEVEMENTS", "key": "[3]", "label": "ЗАЛ СЛАВЫ & ДОСТИЖЕНИЯ", "sub": "13 наград, секретные испытания и трофеи", "color": (255, 185, 60)},
        {"id": "DOJO", "key": "[4]", "label": "ТРЕНИРОВОЧНОЕ ДОДЗЁ", "sub": "Отработка комбо на бессмертных манекенах", "color": (140, 245, 140)},
        {"id": "CUSTOM_GLYPH", "key": "[5]", "label": "КУЗНИЦА СВОИХ ЗНАКОВ", "sub": "Нарисуй и сохрани собственный символ клинка", "color": (235, 130, 255)},
        {"id": "QUIT", "key": "[6]", "label": "ВЫХОД ИЗ ИГРЫ", "sub": "Покинуть темные чертоги подземелья", "color": (240, 75, 75)}
    ]

    btn_w = 560
    btn_h = 60
    start_y = 150
    gap = 72
    cx = W // 2 - btn_w // 2

    for idx, b in enumerate(buttons):
        by = start_y + idx * gap
        rect = pygame.Rect(cx, by, btn_w, btn_h)
        is_hov = (idx == 0) # hover the first button
        draw_pixel_button(screen, rect, b["label"], b["sub"], b["key"], icons[b["id"]], b["color"], is_hov, fonts, anim_time=1.5)

    artifact_dir = r"C:\Users\Parzi\.gemini\antigravity\brain\7d9095d2-1884-4b03-898e-4cb3bb4d9a32"
    out_path = os.path.join(artifact_dir, "pixel_buttons_test.png")
    pygame.image.save(screen, out_path)
    print("Saved preview to:", out_path)

draw_pixel_button_preview()


