"""Davam edən nəticəni (xalı), Coin-ləri, Max Score və alınmış avadanlıqları saxlayan modul."""

import json
import os
from settings import BASE_DIR

SAVE_FILE = os.path.join(BASE_DIR, "save_data.json")


class GameStats:
    """Oyunun bütün statistikasını və daimi irəliləyişini izləyir."""

    def __init__(self, ai_settings) -> None:
        """Yaddaş faylını oxuyur və ilkin vəziyyəti qurur."""
        self.ai_settings = ai_settings
        self.game_active = False

        # Daimi (oyunlar arası qorunan) göstəricilər
        self.score = 0          # Təzə nəticə köhnə nəticənin üzərindən davam edir!
        self.max_score = 0
        self.coins = 0
        self.unlocked_ships = [0]
        self.selected_ship = 0
        self.has_bomb = False
        self.mini_ships = 0     # 0, 1 və ya 2
        self.protect_count = 0  # Alınmış 20s Protect sayı

        # Sessiya daxili göstəricilər
        self.ships_left = ai_settings.base_ship_limit
        self.level = 1
        self.aliens_to_spawn = 0
        self.spawn_timer = 0
        self.boss_spawned_in_level = False
        self.protect_end_ms = 0
        self.last_bomb_ms = -999_999

        self.load_progress()

    def load_progress(self) -> None:
        """save_data.json faylından köhnə nəticəni və coin-ləri yükləyir."""
        if not os.path.exists(SAVE_FILE):
            # Əvvəlki versiyadan high_score.txt varsa onu da nəzərə alırıq
            old_hs = os.path.join(BASE_DIR, "high_score.txt")
            if os.path.exists(old_hs):
                try:
                    with open(old_hs, "r", encoding="utf-8") as f:
                        val = int(f.read().strip())
                        self.score = val
                        self.max_score = val
                except (ValueError, OSError):
                    pass
            return

        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.score = int(data.get("score", 0))
            self.max_score = max(self.score, int(data.get("max_score", 0)))
            self.coins = int(data.get("coins", 0))
            self.unlocked_ships = list(data.get("unlocked_ships", [0]))
            if 0 not in self.unlocked_ships:
                self.unlocked_ships.append(0)
            self.selected_ship = int(data.get("selected_ship", 0))
            if self.selected_ship not in self.unlocked_ships:
                self.selected_ship = 0
            self.has_bomb = bool(data.get("has_bomb", False))
            self.mini_ships = max(0, min(2, int(data.get("mini_ships", 0))))
            self.protect_count = max(0, int(data.get("protect_count", 0)))
        except (OSError, ValueError, TypeError):
            pass

    def save_progress(self) -> None:
        """Bütün nəticə, coin və mağaza alışlarını save_data.json faylına yazır."""
        self.max_score = max(self.max_score, self.score)
        data = {
            "score": self.score,
            "max_score": self.max_score,
            "coins": self.coins,
            "unlocked_ships": sorted(set(self.unlocked_ships)),
            "selected_ship": self.selected_ship,
            "has_bomb": self.has_bomb,
            "mini_ships": self.mini_ships,
            "protect_count": self.protect_count,
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def start_new_round(self, bonus_lives: int = 0) -> None:
        """Yeni raund başladır (self.score sıfırlanmır, köhnə nəticə ilə davam edir!)."""
        self.ships_left = self.ai_settings.base_ship_limit + bonus_lives
        self.level = 1
        self.aliens_to_spawn = 0
        self.spawn_timer = 0
        self.boss_spawned_in_level = False
        self.protect_end_ms = 0
        self.last_bomb_ms = -999_999
