import math
import random
import pygame

class ActiveAbility:
    def __init__(self, x, y, duration):
        self.x = float(x)
        self.y = float(y)
        self.duration = duration
        self.age = 0.0
        self.alive = True

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        self.age += dt
        if self.age >= self.duration:
            self.alive = False

    def draw(self, surface, offset_x=0, offset_y=0):
        pass

    def get_light(self):
        return None

# =========================================================================
# COMPOUND FUSION 1: КРИО-МЕТЕОРИТ [| + V]
# =========================================================================
class GlacialCometFusion(ActiveAbility):
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=0.48)
        self.damage_mult = damage_mult
        self.spawn_y = target_y - 360
        self.has_exploded = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if self.age >= 0.42 and not self.has_exploded:
            self.has_exploded = True
            fx.add_screen_shake(28.0)
            fx.spawn_sparks(self.x, self.y, (140, 230, 255), count=60, speed=420)
            art.add_scorch_mark(self.x, self.y, radius=70)
            sfx.play("crit")
            sfx.play("parry")

            freeze_radius = 280.0
            for en in enemies:
                if not en.alive:
                    continue
                dist = math.hypot(en.x - self.x, en.y - self.y)
                if dist < freeze_radius:
                    dmg = 115.0 * self.damage_mult
                    en.is_frozen = True
                    en.stun_timer = 2.8
                    kb_x = (en.x - self.x) * 3.2
                    kb_y = (en.y - self.y) * 3.2
                    en.take_hit(dmg, kb_x, kb_y, 2.8, True, fx, sfx, spell_tag="КРИО-МЕТЕОР", player=player)
                    art.add_blood_splatter(en.x, en.y, count=14)
                    fx.add_floating_text(f"❄ КРИО-ЗАМОРОЗКА! -{int(dmg)}", en.x, en.y - 45, (140, 230, 255), size=26)

    def draw(self, surface, offset_x=0, offset_y=0):
        t = min(1.0, self.age / 0.42)
        cur_y = self.spawn_y + (self.y - self.spawn_y) * (t ** 2)
        cx = int(self.x + offset_x)
        cy = int(cur_y + offset_y)
        target_alpha = int(180 * t)
        shadow_surf = pygame.Surface((120, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (140, 230, 255, target_alpha), (0, 0, 120, 60), 2)
        surface.blit(shadow_surf, (int(self.x + offset_x - 60), int(self.y + offset_y - 30)))

        if not self.has_exploded:
            pygame.draw.circle(surface, (140, 230, 255), (cx, cy), 24)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 16)
            for i in range(1, 6):
                tail_y = cy - i * 18
                pygame.draw.circle(surface, (100, 180, 255), (cx + random.randint(-6, 6), tail_y), max(2, 24 - i * 4))

    def get_light(self):
        return (self.x, self.y, 260, (140, 220, 255), 0.95)

# =========================================================================
# COMPOUND FUSION 2: ОГНЕННАЯ СИНГУЛЯРНОСТЬ [O + ^]
# =========================================================================
class FirestormVortexFusion(ActiveAbility):
    def __init__(self, x, y, damage_mult):
        super().__init__(x, y, duration=2.4)
        self.damage_mult = damage_mult
        self.pull_radius = 260.0
        self.imploded = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        for en in enemies:
            if not en.alive:
                continue
            dist = math.hypot(self.x - en.x, self.y - en.y)
            if dist < self.pull_radius:
                dx = (self.x - en.x) / max(dist, 1.0)
                dy = (self.y - en.y) / max(dist, 1.0)
                pull_force = (self.pull_radius - dist) * 5.0
                en.vx += dx * pull_force * dt
                en.vy += dy * pull_force * dt
                if random.random() < 0.25:
                    burn_dmg = 8.0 * self.damage_mult
                    en.hp = max(0, en.hp - burn_dmg)
                    fx.spawn_sparks(en.x, en.y, (255, 120, 30), count=2, speed=80)

        if random.random() < 0.7:
            ang = random.uniform(0, 2 * math.pi)
            rad = random.uniform(40, self.pull_radius * 0.7)
            sp_x = self.x + rad * math.cos(ang)
            sp_y = self.y + rad * math.sin(ang)
            fx.spawn_sparks(sp_x, sp_y, (255, 140, 20), count=2, speed=120)

        if self.age >= self.duration and not self.imploded:
            self.imploded = True
            fx.add_screen_shake(22.0)
            fx.spawn_sparks(self.x, self.y, (255, 160, 40), count=55, speed=360)
            art.add_scorch_mark(self.x, self.y, radius=70)
            sfx.play("crit")
            for en in enemies:
                if en.alive and math.hypot(self.x - en.x, self.y - en.y) < 200:
                    dmg = 120.0 * self.damage_mult
                    en.take_hit(dmg, random.uniform(-250, 250), random.uniform(-250, 250), 1.4, True, fx, sfx, spell_tag="ИНФЕРНО", player=player)
                    fx.add_floating_text(f"🔥 ОГНЕННЫЙ КОЛЛАПС! -{int(dmg)}", en.x, en.y - 40, (255, 120, 40), size=28)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        disk_rad = int(38 + 10 * math.sin(self.age * 12))
        acc_surf = pygame.Surface((disk_rad * 2 + 10, disk_rad * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(acc_surf, (255, 80, 20, 160), (disk_rad + 5, disk_rad + 5), disk_rad, 5)
        pygame.draw.circle(acc_surf, (255, 200, 40, 220), (disk_rad + 5, disk_rad + 5), int(disk_rad * 0.7), 3)
        surface.blit(acc_surf, (cx - (disk_rad + 5), cy - (disk_rad + 5)))
        pygame.draw.circle(surface, (20, 10, 5), (cx, cy), 16)
        pygame.draw.circle(surface, (255, 220, 80), (cx, cy), 16, 2)

    def get_light(self):
        return (self.x, self.y, 240, (255, 120, 30), 0.95)

# =========================================================================
# COMPOUND FUSION 3: ГРОМОВОЙ РАСКОЛ [| + Z] (Метеор + Молния)
# =========================================================================
class ThunderMeteorFusion(ActiveAbility):
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=0.45)
        self.damage_mult = damage_mult
        self.spawn_y = target_y - 340
        self.has_exploded = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if self.age >= 0.40 and not self.has_exploded:
            self.has_exploded = True
            fx.add_screen_shake(25.0)
            fx.spawn_sparks(self.x, self.y, (255, 255, 120), count=60, speed=400)
            art.add_scorch_mark(self.x, self.y, radius=65)
            sfx.play("crit")

            # Epic chain lightning arcing from impact to ALL enemies!
            cast_chain_lightning(player, enemies, self.damage_mult * 1.5, fx, sfx)
            for en in enemies:
                if en.alive and math.hypot(en.x - self.x, en.y - self.y) < 220:
                    dmg = 125.0 * self.damage_mult
                    en.take_hit(dmg, (en.x - self.x) * 3.5, (en.y - self.y) * 3.5, 1.4, True, fx, sfx, spell_tag="ГРОЗА", player=player)
                    fx.add_floating_text(f"⚡ ГРОМОВОЙ РАСКОЛ! -{int(dmg)}", en.x, en.y - 45, (255, 255, 100), size=28)

    def draw(self, surface, offset_x=0, offset_y=0):
        t = min(1.0, self.age / 0.40)
        cur_y = self.spawn_y + (self.y - self.spawn_y) * (t ** 2)
        cx = int(self.x + offset_x)
        cy = int(cur_y + offset_y)
        if not self.has_exploded:
            pygame.draw.circle(surface, (255, 255, 140), (cx, cy), 22)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 14)
            for _ in range(4):
                bx = cx + random.randint(-15, 15)
                by = cy + random.randint(-20, 20)
                pygame.draw.line(surface, (180, 240, 255), (cx, cy), (bx, by), 2)

    def get_light(self):
        return (self.x, self.y, 250, (255, 255, 140), 0.95)

# =========================================================================
# COMPOUND FUSION 4: КРОВАВЫЙ ВИХРЬ [O + >] (Черная Дыра + Жатва)
# =========================================================================
class BloodVortexFusion(ActiveAbility):
    def __init__(self, x, y, damage_mult):
        super().__init__(x, y, duration=2.2)
        self.damage_mult = damage_mult
        self.pull_radius = 240.0
        self.has_healed = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        for en in enemies:
            if not en.alive:
                continue
            dist = math.hypot(self.x - en.x, self.y - en.y)
            if dist < self.pull_radius:
                dx = (self.x - en.x) / max(dist, 1.0)
                dy = (self.y - en.y) / max(dist, 1.0)
                en.vx += dx * 280 * dt
                en.vy += dy * 280 * dt

        if self.age >= self.duration and not self.has_healed:
            self.has_healed = True
            fx.add_screen_shake(18.0)
            fx.spawn_sparks(self.x, self.y, (255, 30, 60), count=45, speed=300)
            art.add_blood_splatter(self.x, self.y, count=25)
            sfx.play("parry")
            
            # Massive lifesteal heal for player!
            heal_amount = 45
            player.hp = min(player.max_hp, player.hp + heal_amount)
            fx.add_floating_text(f"+{heal_amount} HP (КРОВАВЫЙ ВИХРЬ)!", player.x, player.y - 45, (80, 255, 140), size=26)

            for en in enemies:
                if en.alive and math.hypot(self.x - en.x, self.y - en.y) < 200:
                    dmg = 85.0 * self.damage_mult
                    en.take_hit(dmg, random.uniform(-180, 180), random.uniform(-180, 180), 1.2, False, fx, sfx, spell_tag="КРОВАВЫЙ ВИХРЬ", player=player)
                    fx.add_floating_text(f"ЖАТВА! -{int(dmg)}", en.x, en.y - 35, (255, 40, 70), size=26)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        disk_rad = int(32 + 8 * math.sin(self.age * 10))
        acc_surf = pygame.Surface((disk_rad * 2 + 10, disk_rad * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(acc_surf, (220, 20, 50, 160), (disk_rad + 5, disk_rad + 5), disk_rad, 4)
        surface.blit(acc_surf, (cx - (disk_rad + 5), cy - (disk_rad + 5)))
        pygame.draw.circle(surface, (30, 5, 10), (cx, cy), 16)
        pygame.draw.circle(surface, (255, 60, 90), (cx, cy), 16, 2)

    def get_light(self):
        return (self.x, self.y, 200, (255, 40, 70), 0.8)

# Standard Abilities
class BlackHoleVortex(ActiveAbility):
    def __init__(self, x, y, damage_mult):
        super().__init__(x, y, duration=2.2)
        self.damage_mult = damage_mult
        self.pull_radius = 240.0
        self.imploded = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        for en in enemies:
            if not en.alive:
                continue
            dist = math.hypot(self.x - en.x, self.y - en.y)
            if dist < self.pull_radius:
                dx = (self.x - en.x) / max(dist, 1.0)
                dy = (self.y - en.y) / max(dist, 1.0)
                en.vx += dx * (self.pull_radius - dist) * 4.5 * dt
                en.vy += dy * (self.pull_radius - dist) * 4.5 * dt
                en.stun_timer = max(en.stun_timer, 0.1)

        if self.age >= self.duration and not self.imploded:
            self.imploded = True
            fx.add_screen_shake(18.0)
            fx.spawn_sparks(self.x, self.y, (200, 100, 255), count=40, speed=320)
            art.add_scorch_mark(self.x, self.y, radius=45)
            sfx.play("crit")
            for en in enemies:
                if en.alive and math.hypot(self.x - en.x, self.y - en.y) < 160:
                    dmg = 28.0 * self.damage_mult
                    en.take_hit(dmg, random.uniform(-200, 200), random.uniform(-200, 200), 1.2, True, fx, sfx, spell_tag="СИНГУЛЯРНОСТЬ", player=player)
                    fx.add_floating_text(f"КОЛЛАПС! -{int(dmg)}", en.x, en.y - 35, (180, 100, 255), size=24)

    def draw(self, surface, offset_x=0, offset_y=0):
        t = self.age / self.duration
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        disk_rad = int(32 + 8 * math.sin(self.age * 10))
        acc_surf = pygame.Surface((disk_rad * 2 + 10, disk_rad * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(acc_surf, (140, 60, 255, 140), (disk_rad + 5, disk_rad + 5), disk_rad, 4)
        surface.blit(acc_surf, (cx - (disk_rad + 5), cy - (disk_rad + 5)))
        core_r = max(6, int(18 * (1.0 - t * 0.3)))
        pygame.draw.circle(surface, (10, 6, 20), (cx, cy), core_r)
        pygame.draw.circle(surface, (220, 160, 255), (cx, cy), core_r, 1)

    def get_light(self):
        return (self.x, self.y, 180, (160, 80, 255), 0.7)


class FireFissure(ActiveAbility):
    def __init__(self, x, y, angle_rad, damage_mult):
        super().__init__(x, y, duration=1.2)
        self.angle_rad = angle_rad
        self.damage_mult = damage_mult
        self.hit_enemies = set()

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        t = self.age / self.duration
        reach = 190.0 * (0.3 + 0.7 * t)
        for _ in range(4):
            ang = self.angle_rad + random.uniform(-0.4, 0.4)
            dist = random.uniform(20, reach)
            px = self.x + dist * math.cos(ang)
            py = self.y + dist * math.sin(ang)
            fx.spawn_sparks(px, py, random.choice([(255, 80, 20), (255, 180, 40), (255, 240, 80)]), count=1, speed=80)
            if random.random() < 0.15:
                art.add_scorch_mark(px, py, radius=18)

        for en in enemies:
            if not en.alive or en in self.hit_enemies:
                continue
            dist = math.hypot(en.x - self.x, en.y - self.y)
            if dist < reach:
                en_ang = math.atan2(en.y - self.y, en.x - self.x)
                if abs((self.angle_rad - en_ang + math.pi) % (2 * math.pi) - math.pi) < 0.55:
                    self.hit_enemies.add(en)
                    dmg = 25.0 * self.damage_mult
                    kb_x = math.cos(self.angle_rad) * 260
                    kb_y = math.sin(self.angle_rad) * 260
                    en.take_hit(dmg, kb_x, kb_y, 0.6, False, fx, sfx, spell_tag="ОГОНЬ", player=player)
                    art.add_blood_splatter(en.x, en.y, count=10)
                    fx.add_floating_text(f"ОГОНЬ! -{int(dmg)}", en.x, en.y - 25, (255, 100, 30), size=24)

    def draw(self, surface, offset_x=0, offset_y=0):
        pass

    def get_light(self):
        reach = 120.0
        lx = self.x + reach * math.cos(self.angle_rad)
        ly = self.y + reach * math.sin(self.angle_rad)
        return (lx, ly, 190, (255, 120, 30), 0.85)


class GlacialStasis(ActiveAbility):
    def __init__(self, target_enemy, damage_mult, player=None):
        extra_freeze = getattr(player, 'freeze_duration_bonus', 0.0) if player else 0.0
        dur = 2.5 + extra_freeze
        super().__init__(target_enemy.x, target_enemy.y, duration=dur)
        self.enemy = target_enemy
        self.damage_mult = damage_mult
        self.enemy.is_frozen = True
        self.enemy.stun_timer = dur

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if not self.enemy.alive or not getattr(self.enemy, 'is_frozen', False):
            self.alive = False
            return
        self.x = self.enemy.x
        self.y = self.enemy.y
        if random.random() < 0.2:
            fx.spawn_sparks(self.x, self.y, (180, 240, 255), count=2, speed=60)
        if self.age >= self.duration:
            self.enemy.is_frozen = False
            fx.spawn_sparks(self.x, self.y, (160, 220, 255), count=18, speed=160)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        c_rad = self.enemy.radius + 10
        ice_poly = [
            (cx - c_rad, cy),
            (cx - c_rad // 2, cy - c_rad),
            (cx + c_rad // 2, cy - c_rad),
            (cx + c_rad, cy),
            (cx + c_rad // 2, cy + c_rad),
            (cx - c_rad // 2, cy + c_rad)
        ]
        ice_surf = pygame.Surface((c_rad * 2 + 10, c_rad * 2 + 10), pygame.SRCALPHA)
        rel_poly = [(px - (cx - c_rad - 5), py - (cy - c_rad - 5)) for px, py in ice_poly]
        pygame.draw.polygon(ice_surf, (140, 220, 255, 140), rel_poly)
        pygame.draw.polygon(ice_surf, (255, 255, 255, 220), rel_poly, 2)
        surface.blit(ice_surf, (cx - c_rad - 5, cy - c_rad - 5))

    def get_light(self):
        return (self.x, self.y, 140, (120, 220, 255), 0.6)


class MeteorImpact(ActiveAbility):
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=0.45)
        self.damage_mult = damage_mult
        self.spawn_y = target_y - 320
        self.has_exploded = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if self.age >= 0.40 and not self.has_exploded:
            self.has_exploded = True
            fx.add_screen_shake(24.0)
            fx.spawn_sparks(self.x, self.y, (255, 140, 40), count=50, speed=380)
            art.add_scorch_mark(self.x, self.y, radius=60)
            sfx.play("crit")

            for en in enemies:
                if not en.alive:
                    continue
                dist = math.hypot(en.x - self.x, en.y - self.y)
                if dist < 180:
                    dmg = 42.0 * self.damage_mult
                    if getattr(en, 'is_frozen', False):
                        dmg *= 2.5
                        en.is_frozen = False
                        fx.add_floating_text(f"★ SHATTER CRIT! -{int(dmg)}", en.x, en.y - 45, (255, 230, 80), size=28)
                        fx.spawn_sparks(en.x, en.y, (180, 240, 255), count=30, speed=260)
                    else:
                        fx.add_floating_text(f"МЕТЕОР! -{int(dmg)}", en.x, en.y - 40, (255, 80, 40), size=26)

                    kb_x = (en.x - self.x) * 4.0
                    kb_y = (en.y - self.y) * 4.0
                    en.take_hit(dmg, kb_x, kb_y, 1.2, True, fx, sfx, spell_tag="МЕТЕОР", player=player)
                    art.add_blood_splatter(en.x, en.y, count=14)

    def draw(self, surface, offset_x=0, offset_y=0):
        t = min(1.0, self.age / 0.40)
        cur_y = self.spawn_y + (self.y - self.spawn_y) * (t ** 2)
        cx = int(self.x + offset_x)
        cy = int(cur_y + offset_y)
        shadow_surf = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (255, 60, 20, int(200 * t)), (0, 0, 80, 40), 2)
        surface.blit(shadow_surf, (int(self.x + offset_x - 40), int(self.y + offset_y - 20)))

        if not self.has_exploded:
            pygame.draw.circle(surface, (255, 120, 30), (cx, cy), 20)
            pygame.draw.circle(surface, (255, 230, 80), (cx, cy), 13)
            for i in range(1, 5):
                tail_y = cy - i * 16
                pygame.draw.circle(surface, (255, 60, 20), (cx + random.randint(-4, 4), tail_y), max(2, 20 - i * 4))

    def get_light(self):
        return (self.x, self.y, 220, (255, 140, 40), 0.9)


def cast_chain_lightning(player, enemies, damage_mult, fx, sfx):
    alive_targets = [e for e in enemies if e.alive]
    if not alive_targets:
        return
    sfx.play("crit")
    fx.add_screen_shake(10.0)
    alive_targets.sort(key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
    chain = [player] + alive_targets[:6]

    for i in range(len(chain) - 1):
        p1 = chain[i]
        p2 = chain[i + 1]
        steps = 8
        for s in range(1, steps + 1):
            t = s / steps
            mid_x = p1.x + (p2.x - p1.x) * t + random.uniform(-18, 18)
            mid_y = p1.y + (p2.y - p1.y) * t + random.uniform(-18, 18)
            fx.spawn_sparks(mid_x, mid_y, (120, 220, 255), count=2, speed=60)
        dmg = 22.0 * damage_mult
        p2.take_hit(dmg, random.uniform(-80, 80), random.uniform(-80, 80), 1.3, False, fx, sfx, spell_tag="МОЛНИЯ", player=player)
        fx.add_floating_text(f"МОЛНИЯ! -{int(dmg)}", p2.x, p2.y - 30, (100, 220, 255), size=24)


def cast_blood_harvest(player, enemies, damage_mult, fx, sfx, art):
    sfx.play("slash")
    healed_total = 0
    for en in enemies:
        if not en.alive:
            continue
        dist = math.hypot(en.x - player.x, en.y - player.y)
        if dist < 220:
            dmg = 18.0 * damage_mult
            en.take_hit(dmg, 0, 0, 0.4, False, fx, sfx, spell_tag="ЖАТВА", player=player)
            art.add_blood_splatter(en.x, en.y, count=16)
            healed = 15
            player.hp = min(player.max_hp, player.hp + healed)
            healed_total += healed
            fx.spawn_sparks(en.x, en.y, (240, 20, 60), count=14, speed=160)

    if healed_total > 0:
        fx.add_floating_text(f"+{healed_total} HP (ВАМПИРИЗМ)!", player.x, player.y - 45, (80, 255, 120), size=24)
        sfx.play("parry")


# =========================================================================
# NEW GLYPH ABILITIES: CROSS [X], TRIANGLE [△], INFINITY [∞], CUSTOM [✦]
# =========================================================================
class CrossSlashAbility(ActiveAbility):
    """[X] Крестовой Разруб: два скрещивающихся лазерных разреза с двойным критом."""
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=0.35)
        self.damage_mult = damage_mult
        self.exploded = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if self.age >= 0.12 and not self.exploded:
            self.exploded = True
            fx.add_screen_shake(16.0)
            fx.spawn_sparks(self.x, self.y, (255, 60, 120), count=40, speed=320)
            art.add_scorch_mark(self.x, self.y, radius=45)
            sfx.play("crit")

            for en in enemies:
                if en.alive and math.hypot(self.x - en.x, self.y - en.y) < 160:
                    dmg = 45.0 * self.damage_mult
                    en.take_hit(dmg, random.uniform(-180, 180), random.uniform(-180, 180), 1.2, True, fx, sfx, spell_tag="РАЗРУБ", player=player)
                    fx.add_floating_text(f"⚔ КРЕСТОВОЙ РАЗРУБ! -{int(dmg)}", en.x, en.y - 40, (255, 60, 120), size=26)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        prog = min(1.0, self.age / 0.18)
        size = int(80 * prog)
        # Draw crossed laser arcs
        pygame.draw.line(surface, (255, 60, 120), (cx - size, cy - size), (cx + size, cy + size), 6)
        pygame.draw.line(surface, (255, 230, 240), (cx - size, cy - size), (cx + size, cy + size), 2)
        pygame.draw.line(surface, (255, 60, 120), (cx - size, cy + size), (cx + size, cy - size), 6)
        pygame.draw.line(surface, (255, 230, 240), (cx - size, cy + size), (cx + size, cy - size), 2)

    def get_light(self):
        return (self.x, self.y, 180, (255, 60, 120), 0.85)


class PrismaticBarrierAbility(ActiveAbility):
    """[△] Эгида Призмы: сияющий треугольный барьер, отражающий врагов и дающий щит."""
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=3.5)
        self.damage_mult = damage_mult
        self.radius = 110.0

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        # Follow player smoothly
        self.x += (player.x - self.x) * 12.0 * dt
        self.y += (player.y - self.y) * 12.0 * dt

        # Repel enemies
        for en in enemies:
            if not en.alive:
                continue
            dist = math.hypot(self.x - en.x, self.y - en.y)
            if dist < self.radius + en.radius:
                dx = (en.x - self.x) / max(dist, 1.0)
                dy = (en.y - self.y) / max(dist, 1.0)
                en.vx += dx * 520 * dt
                en.vy += dy * 520 * dt
                if random.random() < 0.2:
                    dmg = 8.0 * self.damage_mult
                    en.take_hit(dmg, dx * 120, dy * 120, 0.4, False, fx, sfx, spell_tag="ПРИЗМА", player=player)
                    fx.spawn_sparks(en.x, en.y, (100, 255, 200), count=4, speed=140)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        rot = self.age * 2.0
        r = int(self.radius)
        pts = [
            (cx + r * math.cos(rot), cy + r * math.sin(rot)),
            (cx + r * math.cos(rot + 2.094), cy + r * math.sin(rot + 2.094)),
            (cx + r * math.cos(rot + 4.188), cy + r * math.sin(rot + 4.188)),
        ]
        pygame.draw.polygon(surface, (100, 255, 200), pts, 3)
        pygame.draw.circle(surface, (80, 220, 180), (cx, cy), int(r * 0.95), 1)

    def get_light(self):
        return (self.x, self.y, 220, (100, 255, 200), 0.75)


class InfiniteBladeBarrageAbility(ActiveAbility):
    """[∞] Петля Бесконечности: шквал фантомных срезов (Omnislash / Judgement Cut)."""
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=1.2)
        self.damage_mult = damage_mult
        self.slash_timer = 0.0
        self.slashes_done = 0

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        self.slash_timer += dt
        if self.slash_timer >= 0.10 and self.slashes_done < 10:
            self.slash_timer = 0.0
            self.slashes_done += 1
            sfx.play("slash")
            fx.add_screen_shake(7.0)

            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(30, 140)
            sx = self.x + dist * math.cos(ang)
            sy = self.y + dist * math.sin(ang)

            fx.spawn_sparks(sx, sy, (220, 120, 255), count=12, speed=240)
            fx.add_slash(sx, sy, ang + math.pi/2, "SLASH_H", (240, 140, 255))

            for en in enemies:
                if en.alive and math.hypot(sx - en.x, sy - en.y) < 110:
                    dmg = 12.0 * self.damage_mult
                    en.take_hit(dmg, math.cos(ang) * 90, math.sin(ang) * 90, 0.4, False, fx, sfx, spell_tag="ОМНИСЛЕШ", player=player)
                    fx.add_floating_text(f"∞ РАЗРЕЗ! -{int(dmg)}", en.x, en.y - 25, (220, 120, 255), size=20)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        pygame.draw.circle(surface, (220, 120, 255), (cx, cy), 16, 2)

    def get_light(self):
        return (self.x, self.y, 200, (220, 120, 255), 0.8)


class CustomStrikeAbility(ActiveAbility):
    """[✦] Кастомный Знак Игрока: сверхкритический удар древней печати."""
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=0.6)
        self.damage_mult = damage_mult
        self.exploded = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if self.age >= 0.20 and not self.exploded:
            self.exploded = True
            fx.add_screen_shake(24.0)
            fx.spawn_sparks(self.x, self.y, (255, 235, 90), count=60, speed=400)
            art.add_scorch_mark(self.x, self.y, radius=75)
            sfx.play("crit")

            for en in enemies:
                if en.alive and math.hypot(self.x - en.x, self.y - en.y) < 240:
                    dmg = 175.0 * self.damage_mult
                    en.take_hit(dmg, random.uniform(-300, 300), random.uniform(-300, 300), 2.2, True, fx, sfx, spell_tag="ЗНАК ВЛАДЫКИ", player=player)
                    fx.add_floating_text(f"✦ ЗНАК ВЛАДЫКИ! -{int(dmg)}", en.x, en.y - 50, (255, 235, 90), size=30)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        r = int(50 * min(1.0, self.age / 0.20))
        pygame.draw.circle(surface, (255, 235, 90), (cx, cy), r, 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), int(r * 0.6), 2)

    def get_light(self):
        return (self.x, self.y, 260, (255, 235, 90), 0.95)


# =========================================================================
# NEW COMPOUND SYNTHESES:
# 5. [X] + [—] -> ПРОСТРАНСТВЕННЫЙ РАЗРЫВ (Dimensional Rift)
# 6. [△] + [★] -> СВЕТОВОЙ КАТАКЛИЗМ (Holy Prismatic Nova)
# 7. [🛡] + [⌛] -> ХРОНО-СТАЗИС (Absolute Time Freeze)
# =========================================================================
class DimensionalRiftFusion(ActiveAbility):
    """[X] + [—] Пространственный Разрыв: рассекает экран световыми трещинами."""
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=0.8)
        self.damage_mult = damage_mult
        self.cleaved = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if self.age >= 0.25 and not self.cleaved:
            self.cleaved = True
            fx.add_screen_shake(26.0)
            fx.spawn_sparks(self.x, self.y, (120, 240, 255), count=70, speed=420)
            sfx.play("crit")

            for en in enemies:
                if en.alive and math.hypot(self.x - en.x, self.y - en.y) < 280:
                    dmg = 160.0 * self.damage_mult
                    en.take_hit(dmg, random.uniform(-350, 350), random.uniform(-350, 350), 2.0, True, fx, sfx, spell_tag="РАЗРЫВ", player=player)
                    fx.add_floating_text(f"🌌 ПРОСТРАНСТВЕННЫЙ РАЗРЫВ! -{int(dmg)}", en.x, en.y - 45, (120, 240, 255), size=28)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        w = int(220 * min(1.0, self.age / 0.25))
        pygame.draw.line(surface, (140, 240, 255), (cx - w, cy), (cx + w, cy), 8)
        pygame.draw.line(surface, (255, 60, 140), (cx - int(w*0.7), cy - int(w*0.7)), (cx + int(w*0.7), cy + int(w*0.7)), 6)
        pygame.draw.line(surface, (255, 60, 140), (cx - int(w*0.7), cy + int(w*0.7)), (cx + int(w*0.7), cy - int(w*0.7)), 6)

    def get_light(self):
        return (self.x, self.y, 280, (140, 240, 255), 0.95)


class HolyPrismaticNovaFusion(ActiveAbility):
    """[△] + [★] Световой Катаклизм: ослепляющая святая вспышка во всю арену."""
    def __init__(self, target_x, target_y, damage_mult):
        super().__init__(target_x, target_y, duration=1.0)
        self.damage_mult = damage_mult
        self.exploded = False

    def update(self, dt, enemies, player, fx, sfx, art, obstacles=None):
        super().update(dt, enemies, player, fx, sfx, art, obstacles)
        if self.age >= 0.30 and not self.exploded:
            self.exploded = True
            fx.add_screen_shake(28.0)
            fx.spawn_sparks(self.x, self.y, (255, 255, 220), count=80, speed=480)
            sfx.play("crit")

            for en in enemies:
                if en.alive:
                    d = math.hypot(self.x - en.x, self.y - en.y)
                    if d < 360:
                        dmg = 210.0 * self.damage_mult
                        en.take_hit(dmg, (en.x - self.x) * 4.0, (en.y - self.y) * 4.0, 2.5, True, fx, sfx, spell_tag="СВЯТОЙ СВЕТ", player=player)
                        fx.add_floating_text(f"☀ СВЕТОВОЙ КАТАКЛИЗМ! -{int(dmg)}", en.x, en.y - 50, (255, 255, 180), size=30)

    def draw(self, surface, offset_x=0, offset_y=0):
        cx = int(self.x + offset_x)
        cy = int(self.y + offset_y)
        prog = min(1.0, self.age / 0.30)
        rad = int(180 * prog)
        pygame.draw.circle(surface, (255, 255, 220), (cx, cy), rad, 4)
        pygame.draw.circle(surface, (100, 255, 200), (cx, cy), int(rad * 0.7), 3)

    def get_light(self):
        return (self.x, self.y, 350, (255, 255, 220), 1.0)

