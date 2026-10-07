import math
import random
import pygame

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifespan):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.size = size
        self.lifespan = lifespan
        self.age = 0.0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.94
        self.vy *= 0.94
        self.age += dt

    @property
    def alive(self):
        return self.age < self.lifespan

    def draw(self, surface, offset_x=0, offset_y=0):
        fraction = 1.0 - (self.age / self.lifespan)
        cur_size = max(1.0, self.size * fraction)
        alpha_color = self.color
        # Draw small circle
        px = int(self.x + offset_x)
        py = int(self.y + offset_y)
        pygame.draw.circle(surface, alpha_color, (px, py), int(cur_size))

class FloatingText:
    def __init__(self, text, x, y, color, size=24, lifespan=1.1, vy=-45.0, bold=True):
        self.text = text
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.size = size
        self.lifespan = lifespan
        self.age = 0.0
        self.vy = vy
        self.font = pygame.font.SysFont("arial", size, bold=bold)

    def update(self, dt):
        self.y += self.vy * dt
        self.vy *= 0.92
        self.age += dt

    @property
    def alive(self):
        return self.age < self.lifespan

    def draw(self, surface, offset_x=0, offset_y=0):
        fraction = 1.0 - (self.age / self.lifespan)
        render_surf = self.font.render(self.text, True, self.color)
        px = int(self.x + offset_x - render_surf.get_width() // 2)
        py = int(self.y + offset_y - render_surf.get_height() // 2)
        surface.blit(render_surf, (px, py))

class SlashArc:
    def __init__(self, x, y, angle_rad, skill_id, color, duration=0.25):
        self.x = x
        self.y = y
        self.angle_rad = angle_rad
        self.skill_id = skill_id
        self.color = color
        self.duration = duration
        self.age = 0.0

    def update(self, dt):
        self.age += dt

    @property
    def alive(self):
        return self.age < self.duration

    def draw(self, surface, offset_x=0, offset_y=0):
        t = self.age / self.duration
        alpha = int(255 * (1.0 - t))
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)

        # Draw tailored arc depending on skill
        if self.skill_id in ("SLASH_H", "SLASH_V", "UPPERCUT"):
            radius = 65 + int(20 * t)
            arc_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
            sweep = math.pi * 0.75
            start_ang = -sweep / 2
            end_ang = sweep / 2
            
            pts = []
            steps = 14
            for i in range(steps + 1):
                cur_ang = self.angle_rad + start_ang + (end_ang - start_ang) * (i / steps)
                px = (radius + 5) + radius * math.cos(cur_ang)
                py = (radius + 5) + radius * math.sin(cur_ang)
                pts.append((px, py))
            
            if len(pts) >= 2:
                pygame.draw.lines(arc_surf, (*self.color, alpha), False, pts, width=max(2, int(6 * (1.0 - t))))
            surface.blit(arc_surf, (cx - (radius + 5), cy - (radius + 5)))

        elif self.skill_id == "CIRCLE":
            r = int(50 + 40 * t)
            circle_surf = pygame.Surface((r * 2 + 10, r * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (*self.color, alpha), (r + 5, r + 5), r, width=max(2, int(5 * (1.0 - t))))
            surface.blit(circle_surf, (cx - (r + 5), cy - (r + 5)))

        elif self.skill_id == "THRUST":
            # Direct thrust spear line
            length = 90
            tx = cx + length * math.cos(self.angle_rad)
            ty = cy + length * math.sin(self.angle_rad)
            pygame.draw.line(surface, self.color, (cx, cy), (int(tx), int(ty)), width=max(2, int(5 * (1.0 - t))))

class EffectManager:
    def __init__(self):
        self.particles = []
        self.floating_texts = []
        self.slashes = []
        self.screen_shake = 0.0

    def add_screen_shake(self, amount):
        self.screen_shake = min(25.0, self.screen_shake + amount)

    def spawn_sparks(self, x, y, color, count=12, speed=180.0):
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed * 0.3, speed)
            vx = spd * math.cos(ang)
            vy = spd * math.sin(ang)
            size = random.uniform(2.5, 4.5)
            life = random.uniform(0.25, 0.5)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def add_floating_text(self, text, x, y, color, size=24, bold=True):
        self.floating_texts.append(FloatingText(text, x, y, color, size=size, bold=bold))

    def add_slash(self, x, y, angle_rad, skill_id, color):
        self.slashes.append(SlashArc(x, y, angle_rad, skill_id, color))

    def update(self, dt):
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - 35.0 * dt)

        # Update lists
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.alive]

        for s in self.slashes:
            s.update(dt)
        self.slashes = [s for s in self.slashes if s.alive]

    def get_shake_offset(self):
        if self.screen_shake <= 0.1:
            return 0, 0
        ox = random.uniform(-self.screen_shake, self.screen_shake)
        oy = random.uniform(-self.screen_shake, self.screen_shake)
        return int(ox), int(oy)

    def draw(self, surface, offset_x=0, offset_y=0):
        for s in self.slashes:
            s.draw(surface, offset_x, offset_y)
        for p in self.particles:
            p.draw(surface, offset_x, offset_y)
        for ft in self.floating_texts:
            ft.draw(surface, offset_x, offset_y)
