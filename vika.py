import pygame as pg
import sys
from pathlib import Path
import os
import webbrowser

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

screen = Screen()

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
    title_font = pg.font.SysFont("comicsansms", int(screen.width / 25))
    item_font = pg.font.SysFont("comicsansms", int(screen.width / 35))
    small_font = pg.font.Font("comicsansms", int(screen.width / 40))
except:
    title_font = pg.font.Font(None, int(screen.width / 18))
    item_font = pg.font.Font(None, int(screen.width / 28))
    small_font = pg.font.Font(None, int(screen.width / 40))

# Hyperlink configuration
link_text = "Visit Pygame Website"
link_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Пункты меню
# ===== Пункты меню =====
menu_items = ["Продолжить", "Новая игра", "Параметры", "Помощь", "Авторы"]

# ===== Функция рисования текста по центру =====
def draw_text_centered(text, font, y, color=WHITE, shadow=True):
    """Рисует текст по центру экрана по горизонтали на высоте y"""
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    rect.centerx = screen.width // 2
    rect.y = y
    if shadow:
        shadow_surf = font.render(text, True, (30, 30, 30))
        shadow_rect = shadow_surf.get_rect()
        shadow_rect.centerx = screen.width // 2 + 3
        shadow_rect.y = y + 3
        screen.surface.blit(shadow_surf, shadow_rect)
    screen.surface.blit(surf, rect)

# Вычисляем отступы для центрирования списка пунктов
item_height = item_font.get_height()
total_height = len(menu_items) * (item_height + 75)  # 75 – отступ между пунктами
start_y = (screen.height - total_height) // 3 + 25  # немного сместим вниз

# Данные авторов
authors_data = [
    {'name': 'ChatGPT', 'role': 'Главный программист', 'image': 'author1.png'},
    {'name': 'Шедеврум', 'role': 'Художник', 'image': 'author2.png'},
    {'name': 'Альфа-банк', 'role': 'Дизайнер', 'image': 'author3.png'},
    {'name': 'Bendy, Sally Face, Deltarune', 'role': 'Вдохновители', 'image': 'author4.png'},
    {'name': 'Vikyye', 'role': 'Программист', 'image': 'brahbrah.png'},
    {'name': 'Boss Paket', 'role': 'Сценарист/Художник', 'image': 'author4.png'},
    {'name': 'Konyak_Konyakovich', 'role': 'Тестировщик/Сценарист/Никто', 'image': 'author4.png'},
    {'name': 'Порванная записка', 'role': 'ГЕНЕРАЛЬНЫЙ ДИРЕКТОР', 'image': 'torn_paper.png'},
    {'name': 'PonchikPonchik', 'role': 'Помощь/Бизнесмен', 'image': 'vanya.png'}
]

# Загружаем картинки (если нет – заглушка)
author_images = []
for author in authors_data:
    auth_dir = Path(f'{absolute_path}{img_dir}/sprites/authors/{author['image']}')
    if os.path.exists(auth_dir):
        img = pg.image.load(auth_dir)
        img = pg.transform.scale(img, (80, 80))
    else:
        img = pg.Surface((80, 80))
        img.fill(GRAY)
    author_images.append(img)

def draw_menu():
    screen.surface.fill(BLACK)

    if background_og:
        bg_scaled = pg.transform.scale(background_og, (int(screen.width), screen.height))
        # Рисуем фон с учётом бордюров (чтобы сохранить пропорции 4:3)
        screen.surface.blit(bg_scaled, (0, 0))

    # Рисуем заголовок
    title_font_width, title_font_height = title_font.size(name_game)
    draw_text_centered(name_game, title_font, 60, DARK_GRAY, shadow=True)

    # --- Пункты меню (центрированы) ---
    mouse_x, mouse_y = pg.mouse.get_pos()
    for i, item in enumerate(menu_items):
        y = start_y + i * (item_height + 25)
        # Проверка наведения мыши
        click_rect = pg.Rect(screen.width // 2 - 150, y, 300, item_height)
        color = WHITE if click_rect.collidepoint(mouse_x, mouse_y) else DARK_GRAY
        draw_text_centered(item, item_font, y, color, shadow=True)

def draw_authors():
    screen.surface.fill(BLACK)
    draw_text_centered("АВТОРЫ", title_font, 60, WHITE)

    start_y = 130
    spacing = 100
    for i, author in enumerate(authors_data):
        y = start_y + i * spacing
        # Картинка
        img = author_images[i]
        img_rect = img.get_rect(topleft=(150, y - 40))
        screen.surface.blit(img, img_rect)
        # Имя
        name_surf = item_font.render(author['name'], True, WHITE)
        name_rect = name_surf.get_rect(midleft=(260, y - 10))
        screen.surface.blit(name_surf, name_rect)
        # Роль
        role_surf = small_font.render(author['role'], True, GRAY)
        role_rect = role_surf.get_rect(midleft=(260, y + 20))
        screen.surface.blit(role_surf, role_rect)

    # Кнопка "Назад"
    pg.draw.rect(screen.surface, WHITE, (screen.width // 2 - 60, screen.height - 60, 120, 40), 2)
    draw_text_centered("Назад", item_font, screen.height - 40, WHITE)

try:
    bg_dir = Path(f'{absolute_path}{img_dir}/backgrounds/')   # <-- замени на свой путь
    backgrounds = [img for img in bg_dir.iterdir() if img.is_file()]
    background_image = pg.image.load(backgrounds[1])
    background_og = pg.transform.scale(background_image, (int(screen.width), screen.height))
except Exception as e:
    print("Фон не загружен:", e)
    background_og = None

# Основной цикл
clock = pg.time.Clock()

def main_menu():
    running = True
    state = 'MENU'
    fullscreen = True

    while running:
        # Обработка событий
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if state == 'MENU':
                    for i, item in enumerate(menu_items):
                        y = 200 + i * 70
                        # ИСПРАВЛЕНО: используем ширину, а не высоту
                        rect = pg.Rect(screen.width // 2 - 100, y - 20, 200, 40)
                        if rect.collidepoint(mouse_x, mouse_y):
                            if item == "Авторы":
                                state = 'AUTHORS'
                            elif item == "Играть":
                                print("Запуск игры...")
                            elif item == "Помощь":
                                webbrowser.open(link_url)
                            elif item == "Выход":
                                running = False
                            # "Помощь" можно обработать позже
                elif state == 'AUTHORS':
                    back_rect = pg.Rect(screen.width // 2 - 60, screen.height - 60, 120, 40)
                    if back_rect.collidepoint(mouse_x, mouse_y):
                        state = 'MENU'
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False  # <- также закрываем по ESC (РАБОТАЕТ)
                elif event.key == pg.K_F4:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen.update(screen.save_width, screen.save_height)
                    else:
                        new_w = int(screen.width // 1.75)
                        new_h = int(screen.height // 1.75)
                        screen.update(new_w, new_h)
                    if background_og:
                        bg_scaled = pg.transform.scale(background_og, (screen.width, screen.height))

        if state == 'MENU':
            draw_menu()
        elif state == 'AUTHORS':
            draw_authors()

        pg.display.flip()
        clock.tick(FPS)

main_menu()

pg.quit()
sys.exit()