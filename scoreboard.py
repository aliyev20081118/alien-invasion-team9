"""Oyun zamanı xal, max xal, coin-lər, canlar və aktiv bacarıqları göstərən modul."""

import pygame.font
from pygame.sprite import Group
from ship import Ship


class Scoreboard:
    """Hesab və bacarıq göstəricilərini ekranda əks etdirən sinif."""

    def __init__(self, ai_settings, screen, stats, ship) -> None:
        """Xal lövhəsinin atributlarını işə salır."""
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.ai_settings = ai_settings
        self.stats = stats
        self.player_ship = ship

        self.text_color = (235, 242, 255)
        self.gold_color = (250, 204, 21)
        self.cyan_color = (0, 245, 212)
        self.font = pygame.font.SysFont(None, 32, bold=True)
        self.small_font = pygame.font.SysFont(None, 24, bold=True)

        self.prep_all()

    def prep_all(self) -> None:
        """Bütün göstəriciləri yeniləyir."""
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()

    def prep_score(self) -> None:
        """Davam edən cari xalı hazırlayır."""
        score_str = f"XAL: {self.stats.score:,}"
        self.score_image = self.font.render(score_str, True, self.text_color)
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 16

    def prep_high_score(self) -> None:
        """Coins və Max Score məlumatlarını yuxarı mərkəzdə hazırlayır."""
        top_str = f"COINS: {self.stats.coins}   |   MAX SCORE: {self.stats.max_score:,}"
        self.high_score_image = self.font.render(
            top_str, True, self.gold_color
        )
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = 16

    def prep_level(self) -> None:
        """Cari səviyyəni xalın altında hazırlayır."""
        level_str = f"SƏVİYYƏ: {self.stats.level}"
        self.level_image = self.small_font.render(
            level_str, True, self.cyan_color
        )
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 8

    def prep_ships(self) -> None:
        """Qalan canları seçilmiş gəminin mini ikonu ilə göstərir."""
        self.ships = Group()
        max_icons = min(self.stats.ships_left, 8)
        for ship_number in range(max_icons):
            mini_ship = Ship(
                self.ai_settings, self.screen, self.player_ship.ship_index
            )
            mini_ship.image = pygame.transform.smoothscale(
                mini_ship.image, (32, 30)
            )
            mini_ship.rect = mini_ship.image.get_rect()
            mini_ship.rect.x = 15 + ship_number * (mini_ship.rect.width + 6)
            mini_ship.rect.y = 14
            self.ships.add(mini_ship)

    def show_score(self) -> None:
        """Bütün göstəriciləri və aktiv [E]/[F] bacarıq vəziyyətini çəkir."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)

        # Sol üst hissədə [E] Protect və [F] Bomba statusu
        now = pygame.time.get_ticks()
        y_pos = 52

        if now < self.stats.protect_end_ms:
            rem = (self.stats.protect_end_ms - now) / 1000.0
            p_txt = f"[E] PROTECT AKTİV: {rem:.1f}s"
            p_col = (74, 222, 128)
        else:
            p_txt = f"[E] Protect ehtiyatı: {self.stats.protect_count}"
            p_col = (185, 200, 230)

        p_surf = self.small_font.render(p_txt, True, p_col)
        self.screen.blit(p_surf, (16, y_pos))

        if self.player_ship.ship_index == 1 and self.stats.has_bomb:
            elapsed = now - self.stats.last_bomb_ms
            cd = self.ai_settings.bomb_cooldown_ms
            if elapsed >= cd:
                b_txt = "[F] BOMBA HAZIRDIR!"
                b_col = (250, 204, 21)
            else:
                b_txt = f"[F] Bomba yenilənir: {(cd - elapsed) / 1000.0:.1f}s"
                b_col = (170, 180, 200)
            b_surf = self.small_font.render(b_txt, True, b_col)
            self.screen.blit(b_surf, (16, y_pos + 24))
