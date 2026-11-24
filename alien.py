"""Xaotik hərəkət edən Kiber-Viruslar, Boss və +10 Coin dronları modulu."""

import math
import os
import random
import pygame
from pygame.sprite import Sprite
from settings import get_folder_images, load_clean_sprite

_ALIEN_CACHE_LOADED = False
_REGULAR_SURFACES: list[pygame.Surface] = []
_BOSS_SURFACE: pygame.Surface | None = None


def _ensure_alien_surfaces() -> None:
    """alien/ qovluğundakı bütün şəkilləri yükləyir."""
    global _ALIEN_CACHE_LOADED, _REGULAR_SURFACES, _BOSS_SURFACE
    if _ALIEN_CACHE_LOADED:
        return
    _ALIEN_CACHE_LOADED = True

    files = get_folder_images("alien")
    for filepath in files:
        fname = os.path.basename(filepath).lower()
        if "boss" in fname:
            _BOSS_SURFACE = load_clean_sprite(filepath, (130, 108))
        else:
            _REGULAR_SURFACES.append(load_clean_sprite(filepath, (58, 52)))

    if not _REGULAR_SURFACES and _BOSS_SURFACE is not None:
        _REGULAR_SURFACES.append(
            pygame.transform.smoothscale(_BOSS_SURFACE, (58, 52))
        )


class Alien(Sprite):
    """Şaquli və Sideways rejimlərində xaotik hücum edən Kiber-Virus sinfi."""

    def __init__(
        self,
        ai_settings,
        screen,
        is_boss: bool = False,
        is_coin_alien: bool = False,
        sideways: bool = False,
        level: int = 1,
    ) -> None:
        """Virusu seçilmiş oyun rejiminə uyğun başlanğıc nöqtəsində yaradır."""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings
        self.screen_rect = screen.get_rect()
        self.is_boss = is_boss
        self.is_coin_alien = is_coin_alien and not is_boss
        self.sideways = sideways

        _ensure_alien_surfaces()
        raw_surf = self._pick_surface(is_boss)
        self.image = (
            pygame.transform.rotate(raw_surf, 90) if sideways else raw_surf
        )
        self.rect = self.image.get_rect()

        if sideways:
            # Sideways rejimdə viruslar ekranın sağından daxil olub sola uçur
            self.x = float(ai_settings.screen_width + random.randint(10, 50))
            self.y = float(
                random.randint(70, ai_settings.screen_height - self.rect.height - 20)
            )
            self.vx = -ai_settings.alien_fall_speed * (
                0.5 if is_boss else random.uniform(0.9, 1.45)
            )
            self.vy = random.uniform(
                -ai_settings.alien_chaos_speed, ai_settings.alien_chaos_speed
            )
        else:
            # Klassik rejimdə viruslar yuxarıdan daxil olub aşağı düşür
            margin = max(24, self.rect.width)
            max_x = max(margin + 10, ai_settings.screen_width - margin)
            self.x = float(random.randint(24, max_x))
            self.y = float(-self.rect.height - random.randint(5, 45))
            self.vy = ai_settings.alien_fall_speed * (
                0.45 if is_boss else random.uniform(0.80, 1.35)
            )
            self.vx = random.uniform(
                -ai_settings.alien_chaos_speed, ai_settings.alien_chaos_speed
            )

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if is_boss:
            self.wave_amp = 2.4
            self.wave_freq = 0.04
            self.base_points = 100
            self.coin_reward = 40
            self.max_hp = 12 + (level * 2)
        else:
            self.wave_amp = random.uniform(1.5, 4.0)
            self.wave_freq = random.uniform(0.03, 0.09)
            self.base_points = 15 if self.is_coin_alien else 10
            self.coin_reward = 10 if self.is_coin_alien else 2
            self.max_hp = 1

        self.hp = self.max_hp
        self.phase = random.uniform(0.0, 2.0 * math.pi)
        self.ticks = 0
        self.chaos_timer = random.randint(25, 70)

    def _pick_surface(self, is_boss: bool) -> pygame.Surface:
        """Yüklənmiş şəkillərdən uyğun olanını seçir."""
        if is_boss and _BOSS_SURFACE is not None:
            return _BOSS_SURFACE
        if _REGULAR_SURFACES:
            return random.choice(_REGULAR_SURFACES)

        size = (120, 96) if is_boss else (54, 46)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.ellipse(
            surf, (235, 65, 110), (4, 8, size[0] - 8, size[1] - 16)
        )
        return surf

    def update(self) -> None:
        """Virusu xaotik trayektoriya ilə hərəkət etdirir."""
        self.ticks += 1
        self.chaos_timer -= 1

        if self.chaos_timer <= 0:
            self.chaos_timer = random.randint(25, 70)
            limit = self.ai_settings.alien_chaos_speed * 1.4
            if self.sideways:
                self.vy = random.uniform(-limit, limit)
            else:
                self.vx = random.uniform(-limit, limit)

        sway = math.sin(self.ticks * self.wave_freq + self.phase) * self.wave_amp

        if self.sideways:
            self.x += self.vx
            self.y += self.vy + sway
            if self.y <= 56:
                self.y = 56.0
                self.vy = abs(self.vy) + 0.8
            elif self.y + self.rect.height >= self.screen_rect.height - 8:
                self.y = float(self.screen_rect.height - 8 - self.rect.height)
                self.vy = -(abs(self.vy) + 0.8)
        else:
            self.x += self.vx + sway
            self.y += self.vy
            if self.x <= 8:
                self.x = 8.0
                self.vx = abs(self.vx) + 0.8
            elif self.x + self.rect.width >= self.screen_rect.width - 8:
                self.x = float(self.screen_rect.width - 8 - self.rect.width)
                self.vx = -(abs(self.vx) + 0.8)

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw_extras(self) -> None:
        """Boss can zolağını və +10 Coin nişanını çəkir."""
        if self.is_coin_alien:
            pygame.draw.ellipse(
                self.screen, (250, 204, 21), self.rect.inflate(8, 8), width=2
            )
            coin_pos = (self.rect.right - 6, self.rect.top + 6)
            pygame.draw.circle(self.screen, (250, 204, 21), coin_pos, 7)

        if self.max_hp > 1:
            bar_w = self.rect.width - 16
            bar_h = 8
            bar_x = self.rect.left + 8
            bar_y = max(4, self.rect.top - 12)
            ratio = max(0.0, self.hp / self.max_hp)
            pygame.draw.rect(
                self.screen,
                (50, 20, 70),
                (bar_x, bar_y, bar_w, bar_h),
                border_radius=3,
            )
            pygame.draw.rect(
                self.screen,
                (0, 255, 195),
                (bar_x, bar_y, int(bar_w * ratio), bar_h),
                border_radius=3,
            )
