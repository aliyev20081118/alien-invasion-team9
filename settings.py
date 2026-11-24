"""Kiber-Şəbəkə Qoruyucusu oyununun bütün konfiqurasiya parametrləri və səs sistemi."""

import math
import os
import random
import struct
import wave
import pygame

try:
    import cv2
except ImportError:
    cv2 = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mov", ".webm", ".mkv", ".gif")


def get_folder_files(folder_name: str, extensions: tuple[str, ...]) -> list[str]:
    """assets/<qovluq>/ və ya <qovluq>/ içindəki uyğun faylları tapır."""
    search_dirs = [
        os.path.join(BASE_DIR, "assets", folder_name),
        os.path.join(BASE_DIR, folder_name),
    ]
    found_files = []
    for folder in search_dirs:
        if os.path.isdir(folder):
            for fname in sorted(os.listdir(folder)):
                if fname.lower().endswith(extensions):
                    found_files.append(os.path.join(folder, fname))
            if found_files:
                break
    return found_files


def get_folder_images(folder_name: str) -> list[str]:
    """Qovluqdakı bütün şəkil fayllarını qaytarır."""
    return get_folder_files(folder_name, IMAGE_EXTENSIONS)


def find_background_video() -> str | None:
    """Arxa fon videosunu assets/bg/ və ya bg/ daxilində axtarır."""
    videos = get_folder_files("bg", VIDEO_EXTENSIONS)
    return videos[0] if videos else None


def find_background_image() -> str | None:
    """Arxa fon şəklini assets/bg/ və ya assets/ daxilində axtarır."""
    images = get_folder_images("bg")
    if images:
        return images[0]
    for folder in (os.path.join(BASE_DIR, "assets"), BASE_DIR):
        if os.path.isdir(folder):
            for fname in sorted(os.listdir(folder)):
                if fname.lower().endswith(IMAGE_EXTENSIONS) and fname.lower().startswith(
                    ("bg", "background", "cyber", "kosmos", "space")
                ):
                    return os.path.join(folder, fname)
    return None


def load_clean_sprite(filepath: str, size: tuple[int, int]) -> pygame.Surface:
    """Şəkli yükləyir və kənarlardakı qara fonu avtomatik şəffaflaşdırır."""
    raw = pygame.image.load(filepath).convert_alpha()
    w, h = raw.get_size()

    if (
        raw.get_at((0, 0)).a == 0
        and raw.get_at((w - 1, 0)).a == 0
        and raw.get_at((0, h - 1)).a == 0
    ):
        return pygame.transform.smoothscale(raw, size)

    max_dim = 180
    if w > max_dim or h > max_dim:
        ratio = max_dim / max(w, h)
        w = max(1, int(w * ratio))
        h = max(1, int(h * ratio))
        raw = pygame.transform.smoothscale(raw, (w, h))

    surf = raw.copy()
    visited = set()
    stack = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)]
    stack += [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]

    while stack:
        x, y = stack.pop()
        if (x, y) in visited or not (0 <= x < w and 0 <= y < h):
            continue
        visited.add((x, y))
        c = surf.get_at((x, y))
        if c.r < 35 and c.g < 35 and c.b < 35:
            surf.set_at((x, y), (0, 0, 0, 0))
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    return pygame.transform.smoothscale(surf, size)


class Settings:
    """Kiber-Şəbəkə Qoruyucusu oyununun bütün tənzimləmələrini saxlayan sinif."""

    def __init__(self) -> None:
        """Ekran, rəng palitrası, silah və mağaza parametrlərini işə salır."""
        self.screen_width = 1200
        self.screen_height = 800
        # Kiber-Şəbəkə temasına uyğun tünd kiber-göy fon
        self.bg_color = (8, 15, 28)
        self.grid_color = (16, 36, 58)
        self.star_count = 85

        # Arxa fon media dəyişənləri
        self.bg_image: pygame.Surface | None = None
        self.video_cap = None
        self.current_video_frame: pygame.Surface | None = None
        self._video_interval_ms = 33.3
        self._last_video_tick = 0

        # Oyunçu və Bonus 2 (Turbo) parametrləri
        self.base_ship_limit = 3
        self.turbo_multiplier = 2.0

        # Mağaza qiymətləri
        self.bomb_price = 200
        self.mini_ship_price = 200
        self.protect_price = 100
        self.protect_duration_ms = 20_000
        self.bomb_cooldown_ms = 15_000
        self.bomb_max_targets = 3

        # Kiber-İmpuls (Güllə) parametrləri
        self.bullet_width = 5
        self.bullet_height = 20
        self.bullet_color = (0, 255, 195)
        self.bullets_allowed = 6

        # Çətinlik artımı
        self.speedup_scale = 1.10
        self.initialize_dynamic_settings()

    def load_background(self) -> None:
        """Arxa fon videosunu və ya şəklini yükləyir."""
        video_path = find_background_video()
        if video_path and cv2 is not None:
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                self.video_cap = cap
                fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                if fps <= 1 or fps > 60:
                    fps = 30.0
                self._video_interval_ms = 1000.0 / fps
                self.get_background_frame()
                return

        bg_path = find_background_image()
        if bg_path:
            raw_bg = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.smoothscale(
                raw_bg, (self.screen_width, self.screen_height)
            )

    def get_background_frame(self) -> pygame.Surface | None:
        """Videonun növbəti kadrını qaytarır."""
        if self.video_cap is None or cv2 is None:
            return self.bg_image

        now = pygame.time.get_ticks()
        if (
            self.current_video_frame is not None
            and (now - self._last_video_tick) < self._video_interval_ms
        ):
            return self.current_video_frame

        self._last_video_tick = now
        ret, frame = self.video_cap.read()
        if not ret:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video_cap.read()

        if ret:
            resized = cv2.resize(
                frame,
                (self.screen_width, self.screen_height),
                interpolation=cv2.INTER_LINEAR,
            )
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            self.current_video_frame = pygame.image.frombuffer(
                rgb.tobytes(), (self.screen_width, self.screen_height), "RGB"
            ).convert()

        return self.current_video_frame

    def initialize_dynamic_settings(self) -> None:
        """Dəyişən sürət parametrlərini sıfırlayır."""
        self.ship_speed_factor = 6.5
        self.bullet_speed_factor = 12.0
        self.alien_fall_speed = 1.85
        self.alien_chaos_speed = 2.4

    def increase_speed(self) -> None:
        """Növbəti təhlükə dalğasında sürəti artırır."""
        self.ship_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_fall_speed *= self.speedup_scale
        self.alien_chaos_speed *= self.speedup_scale

    def init_sounds(self) -> dict:
        """Kiber səs effektlərini sintez edir və yükləyir."""
        assets_dir = os.path.join(BASE_DIR, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        sound_paths = {
            "laser": os.path.join(assets_dir, "laser.wav"),
            "explosion": os.path.join(assets_dir, "explosion.wav"),
            "level_up": os.path.join(assets_dir, "level_up.wav"),
            "game_over": os.path.join(assets_dir, "game_over.wav"),
            "bg_music": os.path.join(assets_dir, "bg_music.wav"),
        }
        self._generate_default_wavs(sound_paths)

        sounds = {}
        try:
            sounds["laser"] = pygame.mixer.Sound(sound_paths["laser"])
            sounds["laser"].set_volume(0.28)
            sounds["explosion"] = pygame.mixer.Sound(sound_paths["explosion"])
            sounds["explosion"].set_volume(0.42)
            sounds["level_up"] = pygame.mixer.Sound(sound_paths["level_up"])
            sounds["level_up"].set_volume(0.48)
            sounds["game_over"] = pygame.mixer.Sound(sound_paths["game_over"])
            sounds["game_over"].set_volume(0.48)
            pygame.mixer.music.load(sound_paths["bg_music"])
            pygame.mixer.music.set_volume(0.16)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass
        return sounds

    def _generate_default_wavs(self, paths: dict) -> None:
        """WAV faylları yoxdursa avtomatik səs yaradır."""
        sr = 44100
        if not os.path.exists(paths["laser"]):
            frames = [
                struct.pack(
                    "<h",
                    int(
                        14000
                        * (1 - i / (sr * 0.1))
                        * math.sin(2 * math.pi * (1100 - 750 * i / (sr * 0.1)) * (i / sr))
                    ),
                )
                for i in range(int(sr * 0.1))
            ]
            self._write_wav(paths["laser"], sr, b"".join(frames))

        if not os.path.exists(paths["explosion"]):
            rng = random.Random(42)
            frames = [
                struct.pack(
                    "<h",
                    int(16000 * math.exp(-7.5 * (i / sr)) * rng.uniform(-1.0, 1.0)),
                )
                for i in range(int(sr * 0.25))
            ]
            self._write_wav(paths["explosion"], sr, b"".join(frames))

        if not os.path.exists(paths["level_up"]):
            frames = []
            for f in (523.25, 659.25, 783.99, 1046.5):
                for i in range(int(sr * 0.08)):
                    frames.append(
                        struct.pack(
                            "<h", int(14000 * math.sin(2 * math.pi * f * (i / sr)))
                        )
                    )
            self._write_wav(paths["level_up"], sr, b"".join(frames))

        if not os.path.exists(paths["game_over"]):
            frames = []
            for f in (440.0, 349.23, 293.66, 220.0):
                for i in range(int(sr * 0.14)):
                    frames.append(
                        struct.pack(
                            "<h", int(14000 * math.sin(2 * math.pi * f * (i / sr)))
                        )
                    )
            self._write_wav(paths["game_over"], sr, b"".join(frames))

        if not os.path.exists(paths["bg_music"]):
            dur = 3.2
            seq = [73.42, 73.42, 87.31, 82.41]
            step = dur / len(seq)
            frames = []
            for i in range(int(sr * dur)):
                t = i / sr
                freq = seq[min(int(t / step), len(seq) - 1)]
                val = int(5500 * math.sin(2 * math.pi * freq * t))
                frames.append(struct.pack("<h", val))
            self._write_wav(paths["bg_music"], sr, b"".join(frames))

    @staticmethod
    def _write_wav(filepath: str, sample_rate: int, audio_bytes: bytes) -> None:
        """WAV faylını diskə yazır."""
        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_bytes)
