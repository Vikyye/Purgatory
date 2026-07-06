import pygame as pg
import sys
from pathlib import Path

# Инициализация
pg.init()

FPS = 60

name_game = 'Rain in the Fog'
pg.display.set_caption(name_game)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

absolute_path = Path().resolve()
img_dir = Path('/media/images/')
snd_dir = Path('/media/sounds/')

class Screen():
    def __init__(self):
        self.screen_info = pg.display.Info()
        self.width = self.save_width = self.screen_info.current_w
        self.height = self.save_height =  self.screen_info.current_h
        self.set_size(self.width, self.height)

    def set_size(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.surface = pg.display.set_mode((self.width, self.height))

    def update(self, new_width, new_height):
        self.set_size(new_width, new_height)

screen_obj = Screen()

class Object():
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
    def draw(self):
        pass


# Шрифт (по умолчанию)
try:
    title_font = pg.font.SysFont("comicsansms", int(screen_obj.width / 25))
    item_font = pg.font.SysFont("comicsansms", int(screen_obj.width / 35))
except:
    title_font = pg.font.Font(None, int(screen_obj.width / 18))
    item_font = pg.font.Font(None, int(screen_obj.width / 28))

# Пункты меню
# ===== Пункты меню =====
menu_items = ["Продолжить", "Новая игра", "Параметры", "Помощь", "Авторы"]

# ===== Функция рисования текста по центру =====
def draw_text_centered(text, font, y, color=WHITE, shadow=True):
    """Рисует текст по центру экрана по горизонтали на высоте y"""
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    rect.centerx = screen_obj.width // 2
    rect.y = y
    if shadow:
        shadow_surf = font.render(text, True, (30, 30, 30))
        shadow_rect = shadow_surf.get_rect()
        shadow_rect.centerx = screen_obj.width // 2 + 3
        shadow_rect.y = y + 3
        screen_obj.surface.blit(shadow_surf, shadow_rect)
    screen_obj.surface.blit(surf, rect)

# Вычисляем отступы для центрирования списка пунктов
item_height = item_font.get_height()
total_height = len(menu_items) * (item_height + 75)  # 75 – отступ между пунктами
start_y = (screen_obj.height - total_height) // 3 + 25  # немного сместим вниз

try:
    bg_dir = Path(f'{absolute_path}{img_dir}/backgrounds/')   # <-- замени на свой путь
    backgrounds = [img for img in bg_dir.iterdir() if img.is_file()]
    background_image = pg.image.load(backgrounds[1])
    background_og = pg.transform.scale(background_image, (int(screen_obj.width), screen_obj.height))
except Exception as e:
    print("Фон не загружен:", e)
    background_og = None

# Основной цикл

clock = pg.time.Clock()

fullscreen = True

def main_menu():
    running = True
    while running:
        # Обработка событий
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for i, item in enumerate(menu_items):
                    y = start_y + i * (item_height + 25)
                    # Зона клика – шире текста для удобства
                    click_rect = pg.Rect(screen_obj.width // 2 - 150, y, 300, item_height)
                    if click_rect.collidepoint(mouse_x, mouse_y):
                        print(f"Нажато: {item}")  # Здесь можно запускать нужное действие
                        current_menu = item
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False  # <- также закрываем по ESC (РАБОТАЕТ)
                elif event.key == pg.K_F4:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen_obj.update(screen_obj.save_width, screen_obj.save_height)
                    else:
                        new_w = int(screen_obj.width // 1.75)
                        new_h = int(screen_obj.height // 1.75)
                        screen_obj.update(new_w, new_h)
                    if background_og:
                        bg_scaled = pg.transform.scale(background_og, (screen_obj.width, screen_obj.height))


        screen_obj.surface.fill(BLACK)

        if background_og:
            bg_scaled = pg.transform.scale(background_og, (int(screen_obj.width), screen_obj.height))
            # Рисуем фон с учётом бордюров (чтобы сохранить пропорции 4:3)
            screen_obj.surface.blit(bg_scaled, (0, 0))

        # Рисуем заголовок
        title_font_width, title_font_height = title_font.size(name_game)
        draw_text_centered(name_game, title_font, 60, DARK_GRAY, shadow=True)

        # --- Пункты меню (центрированы) ---
        mouse_x, mouse_y = pg.mouse.get_pos()
        for i, item in enumerate(menu_items):
            y = start_y + i * (item_height + 25)
            # Проверка наведения мыши
            click_rect = pg.Rect(screen_obj.width // 2 - 150, y, 300, item_height)
            color = WHITE if click_rect.collidepoint(mouse_x, mouse_y) else DARK_GRAY
            draw_text_centered(item, item_font, y, color, shadow=True)

        pg.display.flip()
        clock.tick(FPS)

def game():
    pass

main_menu()

pg.quit()
sys.exit()