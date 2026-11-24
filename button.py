"""Oyun interfeysi üçün interaktiv düymə modulu."""

import pygame.font


class Button:
    """Ekranda kliklənə bilən düymə yaradan sinif."""

    def __init__(self, ai_settings, screen, msg: str) -> None:
        """Düymənin ölçülərini, rəngini və mətnini hazırlayır."""
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.width, self.height = 220, 56
        self.button_color = (0, 200, 170)
        self.border_color = (180, 255, 245)
        self.text_color = (10, 14, 32)
        self.font = pygame.font.SysFont(None, 44, bold=True)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center
        self.prep_msg(msg)

    def prep_msg(self, msg: str) -> None:
        """Mətni şəkilə çevirib düymənin mərkəzinə yerləşdirir."""
        self.msg_image = self.font.render(
            msg, True, self.text_color, self.button_color
        )
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self) -> None:
        """Düyməni və üzərindəki yazını ekrana çəkir."""
        pygame.draw.rect(
            self.screen, self.button_color, self.rect, border_radius=10
        )
        pygame.draw.rect(
            self.screen, self.border_color, self.rect, width=2, border_radius=10
        )
        self.screen.blit(self.msg_image, self.msg_image_rect)
