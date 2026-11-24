"""Kiber-Şəbəkə Qoruyucusu — Əsas işəsalma modulu."""

import pygame
from pygame.sprite import Group
import game_functions as gf
from game_stats import GameStats
from menu import GameMenu
from scoreboard import Scoreboard
from settings import Settings
from ship import Ship


def run_game() -> None:
    """Oyunu işə salır və 60 FPS əsas dövrəsini idarə edir."""
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()

    ai_settings = Settings()
    sounds = ai_settings.init_sounds()

    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height)
    )
    pygame.display.set_caption("Kiber-Şəbəkə Qoruyucusu — Cyber-Net Defender")

    ai_settings.load_background()

    clock = pygame.time.Clock()
    stats = GameStats(ai_settings)
    ship = Ship(ai_settings, screen, ship_index=stats.selected_ship)
    menu = GameMenu(ai_settings, screen, stats, ship)
    sb = Scoreboard(ai_settings, screen, stats, ship)

    stars = gf.create_starfield(ai_settings)
    bullets = Group()
    aliens = Group()
    effects: list = []

    while True:
        gf.check_events(
            ai_settings,
            screen,
            stats,
            sb,
            menu,
            ship,
            aliens,
            bullets,
            effects,
            sounds,
        )

        if stats.game_active:
            ship.update()
            gf.update_bullets(
                ai_settings,
                screen,
                stats,
                sb,
                ship,
                aliens,
                bullets,
                effects,
                sounds,
            )
            gf.update_aliens(
                ai_settings,
                screen,
                stats,
                sb,
                ship,
                aliens,
                bullets,
                effects,
                sounds,
            )

        gf.update_screen(
            ai_settings,
            screen,
            stats,
            sb,
            menu,
            ship,
            aliens,
            bullets,
            effects,
            stars,
        )

        clock.tick(60)


if __name__ == "__main__":
    run_game()
