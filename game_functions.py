"""Kiber-Şəbəkə Qoruyucusu oyununun hadisə, toqquşma və ekran yeniləmə funksiyaları."""

import math
import random
import sys
from time import sleep
import pygame
from alien import Alien
from bullet import Bullet


def create_starfield(ai_settings) -> list:
    """Kiber-şəbəkə fonu üçün axan rəqəmsal zərrəciklər yaradır."""
    nodes = []
    for _ in range(ai_settings.star_count):
        x = random.randint(0, ai_settings.screen_width)
        y = random.randint(0, ai_settings.screen_height)
        radius = random.choice([1, 2])
        speed = 0.6 + (radius * 0.5)
        color = random.choice([(0, 220, 180), (40, 140, 255), (120, 90, 240)])
        nodes.append([x, float(y), radius, speed, color])
    return nodes


def draw_background(ai_settings, screen, stars: list) -> None:
    """Video/şəkil arxa fonunu və ya Kiber-Şəbəkə torunu çəkir."""
    bg_surface = ai_settings.get_background_frame()
    if bg_surface is not None:
        screen.blit(bg_surface, (0, 0))
        return

    screen.fill(ai_settings.bg_color)
    # Kiber-şəbəkə xətləri
    for x in range(0, ai_settings.screen_width, 60):
        pygame.draw.line(
            screen, ai_settings.grid_color, (x, 0), (x, ai_settings.screen_height)
        )
    for y in range(0, ai_settings.screen_height, 60):
        pygame.draw.line(
            screen, ai_settings.grid_color, (0, y), (ai_settings.screen_width, y)
        )

    for node in stars:
        node[1] += node[3]
        if node[1] > ai_settings.screen_height:
            node[1] = 0.0
            node[0] = random.randint(0, ai_settings.screen_width)
        pygame.draw.circle(screen, node[4], (node[0], int(node[1])), node[2])


def check_events(
    ai_settings,
    screen,
    stats,
    sb,
    menu,
    ship,
    aliens,
    bullets,
    effects: list,
    sounds: dict,
) -> None:
    """Klaviatura və siçan hadisələrini dinləyir."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if ai_settings.video_cap is not None:
                ai_settings.video_cap.release()
            stats.save_progress()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                if ai_settings.video_cap is not None:
                    ai_settings.video_cap.release()
                stats.save_progress()
                sys.exit()

            if not stats.game_active:
                if event.key == pygame.K_TAB:
                    menu.toggle_mode()
                elif event.key in (pygame.K_p, pygame.K_RETURN):
                    start_game(
                        ai_settings,
                        screen,
                        stats,
                        sb,
                        menu,
                        ship,
                        aliens,
                        bullets,
                        effects,
                    )
            else:
                if event.key == pygame.K_RIGHT:
                    ship.moving_right = True
                elif event.key == pygame.K_LEFT:
                    ship.moving_left = True
                elif event.key == pygame.K_UP:
                    ship.moving_up = True
                elif event.key == pygame.K_DOWN:
                    ship.moving_down = True
                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    ship.turbo = True
                elif event.key == pygame.K_SPACE:
                    fire_bullet(ai_settings, screen, stats, ship, bullets, sounds)
                elif event.key == pygame.K_e:
                    activate_protect(ai_settings, stats, ship, effects)
                elif event.key == pygame.K_f:
                    activate_bomb(
                        ai_settings, stats, sb, ship, aliens, effects, sounds
                    )
                elif event.key == pygame.K_ESCAPE:
                    stats.game_active = False
                    stats.save_progress()
                    pygame.mouse.set_visible(True)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                ship.moving_right = False
            elif event.key == pygame.K_LEFT:
                ship.moving_left = False
            elif event.key == pygame.K_UP:
                ship.moving_up = False
            elif event.key == pygame.K_DOWN:
                ship.moving_down = False
            elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                ship.turbo = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not stats.game_active:
                if menu.handle_click(event.pos):
                    start_game(
                        ai_settings,
                        screen,
                        stats,
                        sb,
                        menu,
                        ship,
                        aliens,
                        bullets,
                        effects,
                    )


def start_game(
    ai_settings, screen, stats, sb, menu, ship, aliens, bullets, effects: list
) -> None:
    """Yeni oyunu başladır (nəticə köhnə xalın üzərindən davam edir)."""
    ai_settings.initialize_dynamic_settings()
    pygame.mouse.set_visible(False)

    ship.set_ship_index(stats.selected_ship)
    ship.reset_position(sideways=menu.sideways_mode)

    stats.start_new_round(bonus_lives=ship.specs["bonus_lives"])
    stats.game_active = True

    setup_wave(stats)
    sb.prep_all()

    aliens.empty()
    bullets.empty()
    effects.clear()


def setup_wave(stats) -> None:
    """Növbəti virus dalğasını hazırlayır."""
    stats.aliens_to_spawn = 8 + (stats.level * 2)
    stats.spawn_timer = 15
    stats.boss_spawned_in_level = False


def fire_bullet(
    ai_settings, screen, stats, ship, bullets, sounds: dict
) -> None:
    """Güllə limitini yoxlayır və atəş açır."""
    if len(bullets) >= ai_settings.bullets_allowed:
        return

    bullets.add(Bullet(ai_settings, screen, ship, offset=0))

    if ship.ship_index == 2 and stats.mini_ships >= 1:
        bullets.add(
            Bullet(ai_settings, screen, ship, offset=36, weapon_override="mini")
        )
        if stats.mini_ships >= 2:
            bullets.add(
                Bullet(
                    ai_settings, screen, ship, offset=-36, weapon_override="mini"
                )
            )

    if "laser" in sounds:
        sounds["laser"].play()


def activate_protect(ai_settings, stats, ship, effects: list) -> None:
    """[E] düyməsi ilə 20s Firewall Qalxanını aktivləşdirir."""
    now = pygame.time.get_ticks()
    if now < stats.protect_end_ms:
        return
    if stats.protect_count <= 0:
        add_floating_text(
            effects,
            ship.rect.centerx,
            ship.rect.top - 20,
            "Qalxan yoxdur!",
            (255, 100, 110),
        )
        return

    stats.protect_count -= 1
    stats.protect_end_ms = now + ai_settings.protect_duration_ms
    stats.save_progress()
    add_floating_text(
        effects,
        ship.rect.centerx,
        ship.rect.top - 24,
        "20s FIREWALL QALXANI!",
        (0, 255, 195),
    )


def activate_bomb(
    ai_settings, stats, sb, ship, aliens, effects: list, sounds: dict
) -> None:
    """[F] düyməsi ilə EMP Bomba buraxıb 3 virusu məhv edir."""
    if ship.ship_index != 1 or not stats.has_bomb or len(aliens) == 0:
        return

    now = pygame.time.get_ticks()
    if now - stats.last_bomb_ms < ai_settings.bomb_cooldown_ms:
        return

    stats.last_bomb_ms = now
    targets = sorted(
        aliens.sprites(),
        key=lambda a: math.hypot(
            a.rect.centerx - ship.rect.centerx,
            a.rect.centery - ship.rect.centery,
        ),
    )[: ai_settings.bomb_max_targets]

    effects.append(
        {
            "type": "ring",
            "x": ship.rect.centerx,
            "y": ship.rect.centery,
            "radius": 20,
            "max_radius": 520,
            "color": (80, 180, 255),
        }
    )

    for target in targets:
        damage_alien(target, 5, stats, sb, aliens, effects)

    if "explosion" in sounds:
        sounds["explosion"].play()
    stats.save_progress()


def add_floating_text(
    effects: list, x: int, y: int, text: str, color: tuple[int, int, int]
) -> None:
    """Ekranda yüksələn xal/coin bildirişi yaradır."""
    effects.append(
        {
            "type": "text",
            "x": float(x),
            "y": float(y),
            "text": text,
            "color": color,
            "life": 45,
        }
    )


def damage_alien(
    alien, dmg: int, stats, sb, aliens, effects: list
) -> bool:
    """Virusa zərər vurur; məhv olarsa xal və coin əlavə edir."""
    alien.hp -= dmg
    if alien.hp <= 0:
        if alien in aliens:
            aliens.remove(alien)
        stats.score += alien.base_points
        stats.coins += alien.coin_reward
        stats.max_score = max(stats.max_score, stats.score)

        if alien.is_coin_alien:
            add_floating_text(
                effects,
                alien.rect.centerx,
                alien.rect.centery,
                "+10 COIN!",
                (250, 204, 21),
            )
        else:
            add_floating_text(
                effects,
                alien.rect.centerx,
                alien.rect.centery,
                f"+{alien.base_points}",
                (0, 255, 195),
            )

        sb.prep_score()
        sb.prep_high_score()
        return True
    return False


def update_bullets(
    ai_settings, screen, stats, sb, ship, aliens, bullets, effects: list, sounds: dict
) -> None:
    """Güllələri yeniləyir, ekrandan çıxanları silir və toqquşmanı yoxlayır."""
    bullets.update()

    screen_rect = screen.get_rect()
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0 or bullet.rect.left >= screen_rect.right:
            bullets.remove(bullet)

    collisions = pygame.sprite.groupcollide(bullets, aliens, True, False)
    if collisions:
        destroyed_any = False
        for bullet, hit_aliens in collisions.items():
            for alien in hit_aliens:
                if damage_alien(alien, bullet.damage, stats, sb, aliens, effects):
                    destroyed_any = True

                if bullet.weapon == "rocket":
                    effects.append(
                        {
                            "type": "ring",
                            "x": bullet.rect.centerx,
                            "y": bullet.rect.centery,
                            "radius": 10,
                            "max_radius": 95,
                            "color": (255, 140, 40),
                        }
                    )
                    for other in list(aliens.sprites()):
                        if (
                            math.hypot(
                                other.rect.centerx - bullet.rect.centerx,
                                other.rect.centery - bullet.rect.centery,
                            )
                            <= 95
                        ):
                            if damage_alien(other, 1, stats, sb, aliens, effects):
                                destroyed_any = True

        if destroyed_any and "explosion" in sounds:
            sounds["explosion"].play()
        stats.save_progress()

    if stats.aliens_to_spawn == 0 and len(aliens) == 0:
        bullets.empty()
        ai_settings.increase_speed()
        stats.level += 1
        sb.prep_level()
        setup_wave(stats)
        stats.save_progress()
        if "level_up" in sounds:
            sounds["level_up"].play()


def update_wave_spawner(ai_settings, screen, stats, ship, aliens) -> None:
    """Xaotik virus dalğasını meydana çıxarır."""
    if stats.aliens_to_spawn <= 0:
        return

    if stats.level % 3 == 0 and not stats.boss_spawned_in_level:
        aliens.add(
            Alien(
                ai_settings,
                screen,
                is_boss=True,
                sideways=ship.sideways_mode,
                level=stats.level,
            )
        )
        stats.boss_spawned_in_level = True

    stats.spawn_timer -= 1
    max_simultaneous = min(7, 3 + stats.level)

    if (stats.spawn_timer <= 0 and len(aliens) < max_simultaneous) or len(aliens) == 0:
        aliens.add(
            Alien(
                ai_settings,
                screen,
                is_boss=False,
                is_coin_alien=(random.random() < 0.28),
                sideways=ship.sideways_mode,
                level=stats.level,
            )
        )
        stats.aliens_to_spawn -= 1
        stats.spawn_timer = random.randint(32, 65)


def ship_hit(
    ai_settings, screen, stats, sb, ship, aliens, bullets, effects: list, sounds: dict
) -> None:
    """Gəmi zərbə aldıqda canı azaldır və ya menyuya qaytarır."""
    if "explosion" in sounds:
        sounds["explosion"].play()

    if stats.ships_left > 1:
        stats.ships_left -= 1
        sb.prep_ships()
        aliens.empty()
        bullets.empty()
        effects.clear()
        setup_wave(stats)
        ship.reset_position(sideways=ship.sideways_mode)
        sleep(0.45)
    else:
        stats.ships_left = 0
        sb.prep_ships()
        stats.game_active = False
        stats.save_progress()
        pygame.mouse.set_visible(True)
        if "game_over" in sounds:
            sounds["game_over"].play()


def update_aliens(
    ai_settings, screen, stats, sb, ship, aliens, bullets, effects: list, sounds: dict
) -> None:
    """Virusları hərəkət etdirir və toqquşmaları yoxlayır."""
    update_wave_spawner(ai_settings, screen, stats, ship, aliens)
    aliens.update()

    shield_active = pygame.time.get_ticks() < stats.protect_end_ms

    collided = pygame.sprite.spritecollideany(ship, aliens)
    if collided is not None:
        if shield_active:
            damage_alien(collided, 999, stats, sb, aliens, effects)
            stats.save_progress()
        else:
            ship_hit(
                ai_settings, screen, stats, sb, ship, aliens, bullets, effects, sounds
            )
            return

    screen_rect = screen.get_rect()
    for alien in list(aliens.sprites()):
        escaped = (
            alien.rect.right <= 0
            if ship.sideways_mode
            else alien.rect.top >= screen_rect.bottom
        )
        if escaped:
            if shield_active:
                aliens.remove(alien)
                if stats.aliens_to_spawn > 0:
                    stats.aliens_to_spawn += 1
            else:
                ship_hit(
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
                break


def update_and_draw_effects(screen, effects: list) -> None:
    """Partlayış halqalarını və +10 COIN / xal yazılarını çəkir."""
    font = pygame.font.SysFont(None, 24, bold=True)
    for eff in list(effects):
        if eff["type"] == "ring":
            eff["radius"] += 16
            if eff["radius"] >= eff["max_radius"]:
                effects.remove(eff)
                continue
            pygame.draw.circle(
                screen,
                eff["color"],
                (int(eff["x"]), int(eff["y"])),
                int(eff["radius"]),
                width=3,
            )
        elif eff["type"] == "text":
            eff["y"] -= 1.1
            eff["life"] -= 1
            if eff["life"] <= 0:
                effects.remove(eff)
                continue
            surf = font.render(eff["text"], True, eff["color"])
            screen.blit(surf, surf.get_rect(center=(int(eff["x"]), int(eff["y"]))))


def update_screen(
    ai_settings,
    screen,
    stats,
    sb,
    menu,
    ship,
    aliens,
    bullets,
    effects: list,
    stars: list,
) -> None:
    """Ekrandakı bütün obyektləri və ya menyunu çəkir."""
    draw_background(ai_settings, screen, stars)

    if not stats.game_active:
        menu.draw()
        pygame.display.flip()
        return

    for bullet in bullets.sprites():
        bullet.draw_bullet()

    ship.blitme(mini_ships=stats.mini_ships)

    if pygame.time.get_ticks() < stats.protect_end_ms:
        pygame.draw.circle(
            screen,
            (0, 255, 195),
            ship.rect.center,
            max(ship.rect.width, ship.rect.height) // 2 + 14,
            width=3,
        )

    aliens.draw(screen)
    for alien in aliens.sprites():
        alien.draw_extras()

    update_and_draw_effects(screen, effects)
    sb.show_score()

    pygame.display.flip()
