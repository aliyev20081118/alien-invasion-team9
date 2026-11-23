"""Sprite sinfindən irsiyyət alan Kiber-İmpuls və Raket mərmiləri modulu."""

import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """Gəmidən atılan mərmi və raket sinfi."""

    def __init__(
        self,
        ai_settings,
        screen,
        ship,
        offset: int = 0,
        weapon_override: str | None = None,
    ) -> None:
        """Mərmini seçilmiş silah növünə və oyun rejiminə uyğun yaradır."""
        super().__init__()
        self.screen = screen
        self.sideways = ship.sideways_mode
        self.weapon = weapon_override or ship.specs["weapon"]

        if self.weapon == "rocket":
            w, h = (24, 10) if self.sideways else (10, 24)
            self.damage = 3
            self.speed_factor = ai_settings.bullet_speed_factor * 0.94
            self.color = (255, 200, 60)
            self.glow_color = (255, 65, 20)
        elif self.weapon == "cobalt":
            w, h = (22, 7) if self.sideways else (7, 22)
            self.damage = 2
            self.speed_factor = ai_settings.bullet_speed_factor * 1.18
            self.color = (120, 200, 255)
            self.glow_color = (25, 85, 245)
        elif self.weapon == "mini":
            w, h = (14, 3) if self.sideways else (3, 14)
            self.damage = 1
            self.speed_factor = ai_settings.bullet_speed_factor * 1.1
            self.color = (255, 165, 60)
            self.glow_color = (255, 85, 30)
        else:
            w, h = (20, 5) if self.sideways else (5, 20)
            self.damage = 1
            self.speed_factor = ai_settings.bullet_speed_factor
            self.color = (0, 255, 195)
            self.glow_color = (0, 145, 255)

        self.rect = pygame.Rect(0, 0, w, h)
        if self.sideways:
            self.rect.left = ship.rect.right
            self.rect.centery = ship.rect.centery + offset
        else:
            self.rect.centerx = ship.rect.centerx + offset
            self.rect.top = ship.rect.top

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update(self) -> None:
        """Mərmini şaquli rejimdə yuxarı, Sideways rejimdə isə sağa hərəkət etdirir."""
        if self.sideways:
            self.x += self.speed_factor
            self.rect.x = int(self.x)
        else:
            self.y -= self.speed_factor
            self.rect.y = int(self.y)

    def draw_bullet(self) -> None:
        """Mərmini parlaq kiber-impuls kimi ekranda çəkir."""
        glow_rect = self.rect.inflate(4, 4)
        pygame.draw.rect(self.screen, self.glow_color, glow_rect, border_radius=3)
        pygame.draw.rect(self.screen, self.color, self.rect, border_radius=3)
