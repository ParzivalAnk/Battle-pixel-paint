import os
import math
import random
import pygame

class ArtAssets:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Load pixel art textures
        self.sprite_player = None
        self.sprite_golem = None
        self.sprite_inquisitor = None
        self.sprite_lich = None
        self.sprite_cultist = None
        self.tile_floor = None
        self.title_menu_bg = None
        self._load_pixel_assets()

        # Dynamic lighting darkness mask
        self.light_mask = pygame.Surface((1200, 800), pygame.SRCALPHA)
        self.decals = []

    def _load_pixel_assets(self):
        try:
            if os.path.exists('assets/title_menu_bg.jpg'):
                raw_bg = pygame.image.load('assets/title_menu_bg.jpg').convert()
                self.title_menu_bg = pygame.transform.smoothscale(raw_bg, (1280, 720))
            elif os.path.exists('assets/title_menu_bg.png'):
                raw_bg = pygame.image.load('assets/title_menu_bg.png').convert()
                self.title_menu_bg = pygame.transform.smoothscale(raw_bg, (1280, 720))

            if os.path.exists('assets/player_tuned.png'):
                self.sprite_player = pygame.image.load('assets/player_tuned.png').convert_alpha()
            elif os.path.exists('assets/player.png'):
                self.sprite_player = pygame.image.load('assets/player.png').convert_alpha()

            if os.path.exists('assets/golem_giant.png'):
                self.sprite_golem = pygame.image.load('assets/golem_giant.png').convert_alpha()
            elif os.path.exists('assets/golem.png'):
                self.sprite_golem = pygame.image.load('assets/golem.png').convert_alpha()

            if os.path.exists('assets/inquisitor.png'):
                self.sprite_inquisitor = pygame.image.load('assets/inquisitor.png').convert_alpha()
            elif os.path.exists('assets/stalker.png'):
                self.sprite_inquisitor = pygame.image.load('assets/stalker.png').convert_alpha()

            if os.path.exists('assets/lich.png'):
                self.sprite_lich = pygame.image.load('assets/lich.png').convert_alpha()

            if os.path.exists('assets/cultist.png'):
                self.sprite_cultist = pygame.image.load('assets/cultist.png').convert_alpha()

            if os.path.exists('assets/floor.png'):
                self.tile_floor = pygame.image.load('assets/floor.png').convert()
        except Exception as e:
            print(f"Asset loading info: {e}")

    def add_scorch_mark(self, x, y, radius=50):
        self.decals.append({'x': float(x), 'y': float(y), 'r': int(radius), 'type': 'scorch'})
        if len(self.decals) > 120:
            self.decals.pop(0)

    def add_blood_splatter(self, x, y, count=12):
        for _ in range(count):
            ox = x + random.randint(-35, 35)
            oy = y + random.randint(-35, 35)
            self.decals.append({'x': float(ox), 'y': float(oy), 'r': random.randint(3, 8), 'type': 'blood'})
        if len(self.decals) > 120:
            self.decals = self.decals[-120:]

    def render_decals(self, target_surface, offset_x, offset_y):
        for d in self.decals:
            dx = int(d['x'] + offset_x)
            dy = int(d['y'] + offset_y)
            if -80 <= dx <= 1280 and -80 <= dy <= 880:
                if d['type'] == 'scorch':
                    surf = pygame.Surface((d['r'] * 2, d['r'] * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (15, 12, 10, 160), (d['r'], d['r']), d['r'])
                    pygame.draw.circle(surf, (30, 20, 15, 120), (d['r'], d['r']), int(d['r'] * 0.6))
                    target_surface.blit(surf, (dx - d['r'], dy - d['r']))
                elif d['type'] == 'blood':
                    pygame.draw.circle(target_surface, (140, 15, 25), (dx, dy), d['r'])

    def render_lighting(self, target_surface, light_sources):
        self.light_mask.fill((6, 8, 14, 225))
        for lx, ly, rad, color, intensity in light_sources:
            lx, ly = int(lx), int(ly)
            rad = int(rad)
            cookie = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            steps = 7
            for i in range(steps, 0, -1):
                frac = i / steps
                cur_r = int(rad * frac)
                alpha = int(255 * (1.0 - frac) * intensity)
                pygame.draw.circle(cookie, (color[0], color[1], color[2], alpha), (rad, rad), cur_r)
            self.light_mask.blit(cookie, (lx - rad, ly - rad), special_flags=pygame.BLEND_RGBA_SUB)
        target_surface.blit(self.light_mask, (0, 0))


def draw_player_character(surface, art, x, y, angle_rad, anim_time, weapon_color, is_fumbled, has_iframes, weapon_tier=2):
    x, y = int(x), int(y)

    # Rotating Runic Circle under feet matching weapon color
    rune_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    r_angle = anim_time * 2.5
    for i in range(4):
        a = r_angle + i * (math.pi / 2)
        rx = 32 + 20 * math.cos(a)
        ry = 32 + 20 * math.sin(a)
        pygame.draw.circle(rune_surf, (weapon_color[0], weapon_color[1], weapon_color[2], 130), (int(rx), int(ry)), 3)
    pygame.draw.circle(rune_surf, (weapon_color[0], weapon_color[1], weapon_color[2], 70), (32, 32), 22, 1)
    surface.blit(rune_surf, (x - 32, y - 32))

    # Divine White Aura (Tier 5) or Inferior Red/Orange Ember Aura (Tier 1)
    if weapon_tier == 5:
        # Brilliant Divine White Shimmer
        h_rad = int(24 + 5 * math.sin(anim_time * 6.0))
        pygame.draw.circle(surface, (255, 255, 255), (x, y), h_rad, 2)
        for i in range(4):
            sa = anim_time * 3.0 + i * (math.pi / 2)
            sx = x + int((h_rad + 5) * math.cos(sa))
            sy = y + int((h_rad + 5) * math.sin(sa))
            pygame.draw.circle(surface, (255, 255, 255), (sx, sy), 3)
    elif weapon_tier == 1:
        # Rusty Red-Orange Jagged Ember Ring
        h_rad = int(20 + 3 * math.sin(anim_time * 7.0))
        pygame.draw.circle(surface, (255, 75, 30), (x, y), h_rad, 1)

    if art.sprite_player:
        sp = art.sprite_player
        bob = int(math.sin(anim_time * 6.0) * 2)
        if math.cos(angle_rad) < 0:
            sp = pygame.transform.flip(sp, True, False)
        sw, sh = sp.get_size()
        surface.blit(sp, (x - sw // 2, y - sh // 2 + bob))
    else:
        pygame.draw.circle(surface, (45, 55, 80), (x, y), 16)

    # Orbiting Weapon Focus
    w_orbit_angle = anim_time * 4.0
    orb_dist = 26 if weapon_tier < 5 else 30
    wx = x + int(orb_dist * math.cos(w_orbit_angle))
    wy = y + int(orb_dist * math.sin(w_orbit_angle))
    
    orb_r = 5 if weapon_tier < 4 else (7 if weapon_tier == 4 else 9)
    pygame.draw.circle(surface, weapon_color, (wx, wy), orb_r)
    pygame.draw.circle(surface, (255, 255, 255), (wx, wy), max(2, orb_r - 3))
    if weapon_tier == 5:
        # Cross sparkle on white divine weapon
        pygame.draw.line(surface, (255, 255, 255), (wx - 10, wy), (wx + 10, wy), 2)
        pygame.draw.line(surface, (255, 255, 255), (wx, wy - 10), (wx, wy + 10), 2)


def draw_enemy_sprite(surface, art, en, x, y, anim_time, angle_to_player):
    """Draws any enemy based on their sprite_base, scale, and tint."""
    x, y = int(x), int(y)
    scale = getattr(en, 'scale', 1.0)
    sprite_base = getattr(en, 'sprite_base', 'golem')
    tint = getattr(en, 'tint', (255, 255, 255))
    is_frozen = getattr(en, 'is_frozen', False)

    # Shadow size depends on enemy scale
    shadow_w = int(48 * scale)
    shadow_h = int(18 * scale)
    pygame.draw.ellipse(surface, (8, 10, 15, 170), (x - shadow_w // 2, y + int(en.radius * 0.8), shadow_w, shadow_h))

    # Pick sprite
    sp = None
    if sprite_base == "golem" and art.sprite_golem:
        sp = art.sprite_golem
    elif sprite_base == "inquisitor" and art.sprite_inquisitor:
        sp = art.sprite_inquisitor
    elif sprite_base == "lich" and art.sprite_lich:
        sp = art.sprite_lich
    elif sprite_base == "cultist" and art.sprite_cultist:
        sp = art.sprite_cultist
    elif art.sprite_inquisitor:
        sp = art.sprite_inquisitor

    if sp:
        sw, sh = sp.get_size()
        target_w = max(24, int(sw * (scale / (2.0 if sprite_base == "golem" else 1.0))))
        target_h = max(24, int(sh * (scale / (2.0 if sprite_base == "golem" else 1.0))))
        
        # Scale if needed
        scaled_sp = pygame.transform.scale(sp, (target_w, target_h))
        if math.cos(angle_to_player) < 0:
            scaled_sp = pygame.transform.flip(scaled_sp, True, False)

        # Tint effect for frozen or special factions
        if is_frozen:
            frozen_overlay = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
            frozen_overlay.fill((140, 230, 255, 130))
            scaled_sp.blit(frozen_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif tint != (255, 255, 255):
            tint_overlay = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
            tint_overlay.fill((*tint, 255))
            scaled_sp.blit(tint_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        bob = int(math.sin(anim_time * 4.0 + en.x * 0.01) * 2)
        surface.blit(scaled_sp, (x - target_w // 2, y - target_h // 2 + bob))
    else:
        # Fallback circle
        pygame.draw.circle(surface, tint, (x, y), en.radius)


def draw_obstacle(surface, obs, offset_x, offset_y):
    """Draws stone pillars, altars, and burning braziers."""
    ox = int(obs['x'] + offset_x)
    oy = int(obs['y'] + offset_y)
    r = obs['radius']

    if obs['type'] == 'PILLAR':
        # Stone Pillar with 3D height
        height = 45
        # Shadow
        pygame.draw.ellipse(surface, (8, 10, 15, 180), (ox - r - 4, oy - r // 2 + height // 2, (r + 4) * 2, r + 8))
        # Column body
        pygame.draw.rect(surface, (32, 36, 48), (ox - r, oy - height, r * 2, height))
        pygame.draw.rect(surface, (18, 22, 30), (ox - r, oy - height, r * 2, height), 2)
        # Top circular rim
        pygame.draw.ellipse(surface, (55, 62, 80), (ox - r, oy - height - r // 2, r * 2, r))
        pygame.draw.ellipse(surface, (80, 90, 115), (ox - r, oy - height - r // 2, r * 2, r), 2)
        # Ancient engraved rune on column
        pygame.draw.line(surface, (100, 180, 255), (ox - 4, oy - height + 10), (ox + 4, oy - height + 24), 2)
        pygame.draw.circle(surface, (100, 180, 255), (ox, oy - height + 18), 3)

    elif obs['type'] == 'BRAZIER':
        # Burning Brazier
        pygame.draw.ellipse(surface, (8, 10, 15, 160), (ox - r, oy + 4, r * 2, r))
        pygame.draw.polygon(surface, (45, 48, 58), [(ox - r, oy), (ox + r, oy), (ox + r // 2, oy + 18), (ox - r // 2, oy + 18)])
        # Fire flames
        for i in range(3):
            flame_h = random.randint(12, 22)
            flame_ox = ox + (i - 1) * 6
            pygame.draw.circle(surface, (255, 140, 30), (flame_ox, oy - flame_h // 2), 6)
            pygame.draw.circle(surface, (255, 230, 80), (flame_ox, oy - flame_h // 2), 3)

    elif obs['type'] == 'ALTAR':
        # Sacrificial Stone Altar
        w, h = r * 2, r
        pygame.draw.rect(surface, (38, 42, 54), (ox - w // 2, oy - h // 2, w, h))
        pygame.draw.rect(surface, (18, 20, 28), (ox - w // 2, oy - h // 2, w, h), 2)
        # Glowing Blood rune
        pygame.draw.circle(surface, (220, 40, 60), (ox, oy), 6)


def draw_grimoire_lectern(surface, x, y, anim_time, offset_x, offset_y):
    """Draws an ancient glowing spellbook on a pedestal."""
    lx = int(x + offset_x)
    ly = int(y + offset_y)
    
    # Pedestal
    pygame.draw.rect(surface, (42, 48, 65), (lx - 12, ly - 10, 24, 28))
    pygame.draw.rect(surface, (20, 24, 34), (lx - 12, ly - 10, 24, 28), 2)
    
    # Floating open magical book
    float_y = ly - 28 + int(math.sin(anim_time * 3.5) * 4)
    # Open pages
    pygame.draw.polygon(surface, (240, 230, 200), [(lx, float_y + 4), (lx - 16, float_y - 6), (lx - 16, float_y + 8), (lx, float_y + 14)])
    pygame.draw.polygon(surface, (240, 230, 200), [(lx, float_y + 4), (lx + 16, float_y - 6), (lx + 16, float_y + 8), (lx, float_y + 14)])
    # Glowing magical aura
    pygame.draw.circle(surface, (120, 220, 255), (lx, float_y + 4), 18, 1)


def draw_portal(surface, x, y, anim_time):
    cx, cy = int(x), int(y)
    rad = int(38 + 6 * math.sin(anim_time * 4.0))
    portal_surf = pygame.Surface((rad * 2 + 10, rad * 2 + 10), pygame.SRCALPHA)
    for i in range(3):
        r_cur = rad - i * 8
        pygame.draw.circle(portal_surf, (80, 200, 255, 120 + i * 40), (rad + 5, rad + 5), r_cur, 3)
    surface.blit(portal_surf, (cx - rad - 5, cy - rad - 5))
    pygame.draw.circle(surface, (200, 240, 255), (cx, cy), 12)
