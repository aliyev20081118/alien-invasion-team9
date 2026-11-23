"""Kiber-Şəbəkə Qoruyucusu mağaza, gəmi seçimi və oyun rejimi menyusu."""

import pygame
from ship import SHIP_CATALOG


class GameMenu:
    """CYBER-NET DEFENDER — MENU interfeysini idarə edir."""

    def __init__(self, ai_settings, screen, stats, ship) -> None:
        """Menyu düymələrini və şriftlərini hazırlayır."""
        self.ai_settings = ai_settings
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.stats = stats
        self.ship = ship
        self.sideways_mode = False

        self.title_font = pygame.font.SysFont(None, 58, bold=True)
        self.sub_header_font = pygame.font.SysFont(None, 34, bold=True)
        self.card_title_font = pygame.font.SysFont(None, 32, bold=True)
        self.card_sub_font = pygame.font.SysFont(None, 22)
        self.card_status_font = pygame.font.SysFont(None, 23, bold=True)
        self.small_btn_font = pygame.font.SysFont(None, 23, bold=True)
        self.play_btn_font = pygame.font.SysFont(None, 36, bold=True)
        self.protect_btn_font = pygame.font.SysFont(None, 26, bold=True)
        self.footer_font = pygame.font.SysFont(None, 22, bold=True)
        self.toast_font = pygame.font.SysFont(None, 25, bold=True)

        cx = self.screen_rect.centerx
        card_w, card_h = 330, 240
        gap = 36
        start_x = cx - (card_w * 3 + gap * 2) // 2
        cards_y = 165

        self.card_rects = [
            pygame.Rect(start_x + i * (card_w + gap), cards_y, card_w, card_h)
            for i in range(3)
        ]

        c2 = self.card_rects[1]
        self.bomb_btn_rect = pygame.Rect(c2.x, c2.bottom + 12, c2.width, 42)

        c3 = self.card_rects[2]
        self.mini_btn_rect = pygame.Rect(c3.x, c3.bottom + 12, c3.width, 42)

        # Sol tərəfdə Rejim seçimi düyməsi (Bonus 1: Sideways Shooter)
        c1 = self.card_rects[0]
        self.mode_btn_rect = pygame.Rect(c1.x, c1.bottom + 12, c1.width, 42)

        self.play_btn_rect = pygame.Rect(0, 0, 320, 54)
        self.play_btn_rect.centerx = cx
        self.play_btn_rect.top = self.bomb_btn_rect.bottom + 24

        self.protect_btn_rect = pygame.Rect(0, 0, 420, 44)
        self.protect_btn_rect.centerx = cx
        self.protect_btn_rect.top = self.play_btn_rect.bottom + 12

        self.status_message = ""
        self.status_color = (0, 255, 195)
        self.status_expire_ms = 0

    def set_toast(self, text: str, color: tuple[int, int, int]) -> None:
        """Qısa bildiriş mesajı göstərir."""
        self.status_message = text
        self.status_color = color
        self.status_expire_ms = pygame.time.get_ticks() + 2400

    def toggle_mode(self) -> None:
        """Şaquli və Sideways (Üfüqi) oyun rejimləri arasında keçid edir."""
        self.sideways_mode = not self.sideways_mode
        mode_name = (
            "Sideways Shooter (Üfüqi)"
            if self.sideways_mode
            else "Klassik Müdafiə (Şaquli)"
        )
        self.set_toast(f"Rejim dəyişdirildi: {mode_name}", (0, 255, 195))

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Menyu kliklərini emal edir."""
        for idx, rect in enumerate(self.card_rects):
            if rect.collidepoint(pos):
                self._on_ship_card_click(idx)
                return False

        if self.mode_btn_rect.collidepoint(pos):
            self.toggle_mode()
            return False

        if self.bomb_btn_rect.collidepoint(pos):
            self._buy_bomb()
            return False

        if self.mini_btn_rect.collidepoint(pos):
            self._buy_mini_ship()
            return False

        if self.protect_btn_rect.collidepoint(pos):
            self._buy_protect()
            return False

        if self.play_btn_rect.collidepoint(pos):
            return True

        return False

    def _on_ship_card_click(self, idx: int) -> None:
        """Gəmini seçir və ya Coin ilə alır."""
        spec = SHIP_CATALOG[idx]
        if idx in self.stats.unlocked_ships:
            self.stats.selected_ship = idx
            self.ship.set_ship_index(idx)
            self.stats.save_progress()
            self.set_toast(f"{spec['title']} seçildi!", (0, 255, 195))
        else:
            price = spec["price"]
            if self.stats.coins >= price:
                self.stats.coins -= price
                self.stats.unlocked_ships.append(idx)
                self.stats.selected_ship = idx
                self.ship.set_ship_index(idx)
                self.stats.save_progress()
                self.set_toast(
                    f"{spec['title']} alındı və seçildi!", (0, 255, 195)
                )
            else:
                self.set_toast(
                    f"Daha {price - self.stats.coins} Coin lazımdır!",
                    (255, 100, 110),
                )

    def _buy_bomb(self) -> None:
        """2-ci gəmi üçün EMP Bomba alır."""
        if self.stats.has_bomb:
            self.set_toast(
                "EMP Bomba artıq alınıb! [F] düyməsi ilə işlədin.",
                (250, 204, 21),
            )
            return
        if self.stats.coins >= self.ai_settings.bomb_price:
            self.stats.coins -= self.ai_settings.bomb_price
            self.stats.has_bomb = True
            self.stats.save_progress()
            self.set_toast("EMP Bomba alındı! ([F] düyməsi)", (0, 255, 195))
        else:
            self.set_toast(
                f"Bomba üçün {self.ai_settings.bomb_price} Coin lazımdır!",
                (255, 100, 110),
            )

    def _buy_mini_ship(self) -> None:
        """3-cü gəmi üçün Mini Dron alır (0/2 -> 2/2)."""
        if self.stats.mini_ships >= 2:
            self.set_toast("Hər 2 Mini Dron artıq alınıb!", (250, 204, 21))
            return
        if self.stats.coins >= self.ai_settings.mini_ship_price:
            self.stats.coins -= self.ai_settings.mini_ship_price
            self.stats.mini_ships += 1
            self.stats.save_progress()
            self.set_toast(
                f"Mini Dron alındı! ({self.stats.mini_ships}/2)", (0, 255, 195)
            )
        else:
            self.set_toast(
                f"Mini Dron üçün {self.ai_settings.mini_ship_price} Coin lazımdır!",
                (255, 100, 110),
            )

    def _buy_protect(self) -> None:
        """20s Firewall Qalxanı alır ([E])."""
        if self.stats.coins >= self.ai_settings.protect_price:
            self.stats.coins -= self.ai_settings.protect_price
            self.stats.protect_count += 1
            self.stats.save_progress()
            self.set_toast(
                f"20s Firewall Qalxanı alındı! ({self.stats.protect_count} ədəd)",
                (0, 255, 195),
            )
        else:
            self.set_toast(
                f"Qalxan üçün {self.ai_settings.protect_price} Coin lazımdır!",
                (255, 100, 110),
            )

    def draw(self) -> None:
        """Menyu ekranını çəkir."""
        cx = self.screen_rect.centerx

        title_surf = self.title_font.render(
            "KIBER-ŞƏBƏKƏ QORUYUCUSU — MENU", True, (0, 255, 195)
        )
        title_rect = title_surf.get_rect(centerx=cx, top=36)
        self.screen.blit(title_surf, title_rect)

        info_text = (
            f"Coins: {self.stats.coins}   |   "
            f"Davam Edən Nəticə: {self.stats.score}   |   "
            f"Max Score: {self.stats.max_score}"
        )
        info_surf = self.sub_header_font.render(
            info_text, True, (250, 204, 21)
        )
        info_rect = info_surf.get_rect(centerx=cx, top=title_rect.bottom + 14)
        self.screen.blit(info_surf, info_rect)

        for idx, rect in enumerate(self.card_rects):
            self._draw_ship_card(idx, rect)

        self._draw_sub_buttons()

        pygame.draw.rect(
            self.screen, (16, 155, 115), self.play_btn_rect, border_radius=12
        )
        play_surf = self.play_btn_font.render(
            "OYUNA BAŞLA", True, (255, 255, 255)
        )
        self.screen.blit(
            play_surf, play_surf.get_rect(center=self.play_btn_rect.center)
        )

        pygame.draw.rect(
            self.screen, (34, 52, 78), self.protect_btn_rect, border_radius=10
        )
        pygame.draw.rect(
            self.screen,
            (0, 210, 175),
            self.protect_btn_rect,
            width=2,
            border_radius=10,
        )
        prot_label = f"20s Firewall Qalxanı Al — {self.ai_settings.protect_price} Coin ([E])"
        if self.stats.protect_count > 0:
            prot_label += f"  [{self.stats.protect_count}]"
        prot_surf = self.protect_btn_font.render(
            prot_label, True, (220, 240, 255)
        )
        self.screen.blit(
            prot_surf, prot_surf.get_rect(center=self.protect_btn_rect.center)
        )

        footer_text = (
            "[TAB] Rejim Dəyiş  |  [Shift] Turbo 2x  |  "
            "[F] EMP Bomba  |  [E] 20s Qalxan  |  Coin virus: +10 coin"
        )
        footer_surf = self.footer_font.render(
            footer_text, True, (180, 205, 225)
        )
        footer_rect = footer_surf.get_rect(
            centerx=cx, top=self.protect_btn_rect.bottom + 16
        )
        self.screen.blit(footer_surf, footer_rect)

        if self.status_message and pygame.time.get_ticks() < self.status_expire_ms:
            toast_surf = self.toast_font.render(
                self.status_message, True, self.status_color
            )
            self.screen.blit(
                toast_surf,
                toast_surf.get_rect(centerx=cx, top=footer_rect.bottom + 12),
            )

    def _draw_ship_card(self, idx: int, rect: pygame.Rect) -> None:
        """Gəmi seçim kartını çəkir."""
        spec = SHIP_CATALOG[idx]
        is_selected = self.stats.selected_ship == idx
        is_unlocked = idx in self.stats.unlocked_ships

        pygame.draw.rect(self.screen, (14, 24, 42), rect, border_radius=14)
        border_col = (0, 255, 195) if is_selected else (55, 85, 125)
        pygame.draw.rect(
            self.screen,
            border_col,
            rect,
            width=3 if is_selected else 2,
            border_radius=14,
        )

        img_box = pygame.Rect(0, 0, 74, 74)
        img_box.centerx = rect.centerx
        img_box.top = rect.top + 18
        pygame.draw.rect(self.screen, (10, 16, 30), img_box, border_radius=8)
        preview = self.ship.previews[idx]
        self.screen.blit(preview, preview.get_rect(center=img_box.center))

        name_surf = self.card_title_font.render(
            spec["title"], True, (240, 248, 255)
        )
        name_rect = name_surf.get_rect(
            centerx=rect.centerx, top=img_box.bottom + 14
        )
        self.screen.blit(name_surf, name_rect)

        sub_surf = self.card_sub_font.render(
            spec["subtitle"], True, (165, 190, 215)
        )
        sub_rect = sub_surf.get_rect(
            centerx=rect.centerx, top=name_rect.bottom + 8
        )
        self.screen.blit(sub_surf, sub_rect)

        if is_selected:
            status_text, status_col = "SEÇİLİB", (0, 255, 195)
        elif is_unlocked:
            status_text, status_col = "ALINIB (Seçmək üçün kliklə)", (250, 204, 21)
        else:
            status_text = f"{spec['price']} Coin (Almaq üçün kliklə)"
            status_col = (130, 190, 255)

        st_surf = self.card_status_font.render(status_text, True, status_col)
        self.screen.blit(
            st_surf, st_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 18)
        )

    def _draw_sub_buttons(self) -> None:
        """Rejim, Bomba və Mini Dron düymələrini çəkir."""
        # 1. Rejim düyməsi (Sideways / Şaquli)
        pygame.draw.rect(
            self.screen, (34, 52, 78), self.mode_btn_rect, border_radius=9
        )
        pygame.draw.rect(
            self.screen, (0, 210, 175), self.mode_btn_rect, width=2, border_radius=9
        )
        mode_txt = (
            "Rejim: Sideways Shooter (Üfüqi)"
            if self.sideways_mode
            else "Rejim: Klassik (Şaquli)"
        )
        m_surf = self.small_btn_font.render(mode_txt, True, (0, 255, 195))
        self.screen.blit(m_surf, m_surf.get_rect(center=self.mode_btn_rect.center))

        # 2. EMP Bomba düyməsi
        pygame.draw.rect(
            self.screen, (34, 52, 78), self.bomb_btn_rect, border_radius=9
        )
        pygame.draw.rect(
            self.screen, (70, 100, 140), self.bomb_btn_rect, width=2, border_radius=9
        )
        bomb_txt = (
            "EMP Bomba Alınıb — [F]"
            if self.stats.has_bomb
            else f"EMP Bomba Al — {self.ai_settings.bomb_price} Coin"
        )
        b_col = (0, 255, 195) if self.stats.has_bomb else (205, 220, 240)
        b_surf = self.small_btn_font.render(bomb_txt, True, b_col)
        self.screen.blit(b_surf, b_surf.get_rect(center=self.bomb_btn_rect.center))

        # 3. Mini Dron düyməsi
        pygame.draw.rect(
            self.screen, (34, 52, 78), self.mini_btn_rect, border_radius=9
        )
        pygame.draw.rect(
            self.screen, (70, 100, 140), self.mini_btn_rect, width=2, border_radius=9
        )
        if self.stats.mini_ships < 2:
            mini_txt = f"Mini Dron Al — {self.ai_settings.mini_ship_price} ({self.stats.mini_ships}/2)"
            mini_col = (205, 220, 240)
        else:
            mini_txt = "Mini Dronlar Tam (2/2)"
            mini_col = (0, 255, 195)
        d_surf = self.small_btn_font.render(mini_txt, True, mini_col)
        self.screen.blit(d_surf, d_surf.get_rect(center=self.mini_btn_rect.center))
