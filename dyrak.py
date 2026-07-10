import pygame
import random
import sys
import math

# ---------- ИНИЦИАЛИЗАЦИЯ ----------
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Дурак (1x1) с битой и рисунком масти")
clock = pygame.time.Clock()
FPS = 60

# ---------- ЦВЕТА ----------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 80, 0)
GOLD = (255, 215, 0)
LIGHT_GOLD = (255, 230, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
DARK_BLUE = (10, 10, 40)
BRIGHT_RED = (200, 0, 0)

# ---------- КАРТЫ ----------
RANKS = ['6', '7', '8', '9', '10', 'В', 'Д', 'К', 'Т']
SUITS = ['♠', '♣', '♦', '♥']
SUIT_COLORS = {'♠': BLACK, '♣': BLACK, '♦': RED, '♥': RED}
SUIT_SYMBOLS = {'♠': '♠', '♣': '♣', '♦': '♦', '♥': '♥'}

CARD_WIDTH = 90
CARD_HEIGHT = 130
CARD_SPACING = 25
HAND_Y_PLAYER = HEIGHT - CARD_HEIGHT - 40
HAND_Y_BOT = 40
TABLE_Y = HEIGHT // 2 - CARD_HEIGHT // 2
DISCARD_Y = HEIGHT // 2 + CARD_HEIGHT // 2 + 20

# ---------- ШРИФТЫ ----------
font_hud = pygame.font.Font(None, 28)
font_hud_big = pygame.font.Font(None, 36)
font_hud_title = pygame.font.Font(None, 24)
font_hud_value = pygame.font.Font(None, 30)
font_card_rank = pygame.font.Font(None, 28)
font_card_suit = pygame.font.SysFont('Arial', 100, bold=True)
font_trump_label = pygame.font.Font(None, 36)

# ---------- КАРТЫ ----------
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.rank_val = RANKS.index(rank)
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.speed = 0.3
        self.animating = False

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def set_target(self, tx, ty):
        self.target_x = tx
        self.target_y = ty
        self.animating = True

    def update_animation(self):
        if self.animating:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)
            if dist < 2:
                self.x = self.target_x
                self.y = self.target_y
                self.animating = False
            else:
                self.x += dx * self.speed
                self.y += dy * self.speed

class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for r in RANKS for s in SUITS]
        random.shuffle(self.cards)
        self.trump_suit = random.choice(SUITS)

    def deal(self, n):
        dealt = []
        for _ in range(n):
            if self.cards:
                dealt.append(self.cards.pop())
        return dealt

    def is_empty(self):
        return len(self.cards) == 0

# ---------- ИГРОКИ ----------
class Player:
    def __init__(self, name, is_bot=False):
        self.name = name
        self.hand = []
        self.is_bot = is_bot
        self.is_out = False

    def add_cards(self, cards):
        self.hand.extend(cards)

    def remove_card(self, card):
        self.hand.remove(card)

    def can_beat(self, card, trump_suit):
        result = []
        for c in self.hand:
            if c.suit == trump_suit:
                result.append(c)
            elif c.suit == card.suit and c.rank_val > card.rank_val:
                result.append(c)
        return result

    def choose_best_beat(self, card, trump_suit):
        possible = self.can_beat(card, trump_suit)
        if not possible:
            return None
        if card.suit != trump_suit:
            same_suit = [c for c in possible if c.suit == card.suit]
            if same_suit:
                same_suit.sort(key=lambda c: c.rank_val)
                return same_suit[0]
            trump_cards = [c for c in possible if c.suit == trump_suit]
            if trump_cards:
                trump_cards.sort(key=lambda c: c.rank_val)
                if trump_cards[0].rank_val <= RANKS.index('10'):
                    return trump_cards[0]
                else:
                    return None
        else:
            trump_cards = [c for c in possible if c.suit == trump_suit and c.rank_val > card.rank_val]
            if trump_cards:
                trump_cards.sort(key=lambda c: c.rank_val)
                return trump_cards[0]
        return None

    def choose_attack_card(self, game):
        """Выбор карты для атаки (бот). Подкидывает только карты тех же рангов, что на столе."""
        hand = self.hand
        if not hand:
            return None
        # Собираем все ранги на столе (атакующие + защитные + анимированные)
        ranks = []
        for attack, defense in game.table:
            ranks.append(attack.rank)
            if defense:
                ranks.append(defense.rank)
        for card in game.table_animations:
            ranks.append(card.rank)
        ranks = list(set(ranks))
        if ranks:
            possible = [c for c in hand if c.rank in ranks]
            if possible:
                possible.sort(key=lambda c: c.rank_val)
                return possible[0]
            return None
        # Стол пуст – кладём самую младшую
        hand.sort(key=lambda c: c.rank_val)
        return hand[0]

# ---------- ИГРА ----------
class Game:
    def __init__(self):
        self.deck = Deck()
        self.trump_suit = self.deck.trump_suit
        self.player = Player("Игрок")
        self.bot = Player("Бот", is_bot=True)
        self.players = [self.player, self.bot]
        self.attacker = None
        self.defender = None
        self.table = []
        self.table_animations = []
        self.discard_pile = []
        self.turn = 'attack'
        self.game_over = False
        self.winner = None
        self.message = ""
        self.waiting_for_action = False
        self.bot_thinking = False
        self.deal_animation = False
        self.animating_cards = []
        self.player_score = 0
        self.bot_score = 0
        self.level = 1
        self.coins = 0
        self.refill_delay = 0
        self.refill_triggered = False
        self.start_round()

    def deal_cards(self):
        for _ in range(6):
            cards = self.deck.deal(1)
            if cards:
                self.player.add_cards(cards)
                cards[0].set_target(WIDTH//2, HAND_Y_PLAYER)
                self.animating_cards.append(cards[0])
            cards = self.deck.deal(1)
            if cards:
                self.bot.add_cards(cards)
                cards[0].set_target(WIDTH//2, HAND_Y_BOT)
                self.animating_cards.append(cards[0])
        while len(self.player.hand) < 6 and not self.deck.is_empty():
            cards = self.deck.deal(1)
            if cards:
                self.player.add_cards(cards)
                cards[0].set_target(WIDTH//2, HAND_Y_PLAYER)
                self.animating_cards.append(cards[0])
        while len(self.bot.hand) < 6 and not self.deck.is_empty():
            cards = self.deck.deal(1)
            if cards:
                self.bot.add_cards(cards)
                cards[0].set_target(WIDTH//2, HAND_Y_BOT)
                self.animating_cards.append(cards[0])
        self.update_card_positions()

    def update_card_positions(self):
        n = len(self.player.hand)
        if n > 0:
            total_width = n * CARD_WIDTH + (n - 1) * CARD_SPACING
            start_x = (WIDTH - total_width) // 2
            for i, card in enumerate(self.player.hand):
                card.target_x = start_x + i * (CARD_WIDTH + CARD_SPACING)
                card.target_y = HAND_Y_PLAYER
                card.animating = True
        n = len(self.bot.hand)
        if n > 0:
            total_width = n * CARD_WIDTH + (n - 1) * CARD_SPACING
            start_x = (WIDTH - total_width) // 2
            for i, card in enumerate(self.bot.hand):
                card.target_x = start_x + i * (CARD_WIDTH + CARD_SPACING)
                card.target_y = HAND_Y_BOT
                card.animating = True

    def refill_hands(self):
        added = False
        if len(self.player.hand) < 6:
            while len(self.player.hand) < 6 and not self.deck.is_empty():
                cards = self.deck.deal(1)
                if cards:
                    self.player.add_cards(cards)
                    self.animating_cards.append(cards[0])
                    added = True
        if len(self.bot.hand) < 6:
            while len(self.bot.hand) < 6 and not self.deck.is_empty():
                cards = self.deck.deal(1)
                if cards:
                    self.bot.add_cards(cards)
                    self.animating_cards.append(cards[0])
                    added = True
        self.update_card_positions()
        if self.animating_cards:
            self.deal_animation = True
            self.waiting_for_action = False
        else:
            if not self.deal_animation:
                self.waiting_for_action = (not self.attacker.is_bot)
                self.message = f"Ход {self.attacker.name}"

    def start_round(self):
        self.deal_cards()
        self.deal_animation = True
        self.attacker = self.player
        self.defender = self.bot
        self.table = []
        self.table_animations = []
        self.discard_pile = []
        self.turn = 'attack'
        self.waiting_for_action = False
        self.message = "Раздача карт..."

    def update_animation(self):
        all_finished = True
        for card in self.animating_cards:
            card.update_animation()
            if card.animating:
                all_finished = False
        for card in self.table_animations:
            card.update_animation()
            if card.animating:
                all_finished = False
        if self.deal_animation and all_finished:
            self.deal_animation = False
            if not self.waiting_for_action and not self.game_over:
                self.waiting_for_action = (not self.attacker.is_bot)
                self.message = f"Ход {self.attacker.name}"
            self.animating_cards.clear()
            self.check_win()
        if self.table_animations and all_finished:
            for card in self.table_animations:
                if self.table and self.table[-1][1] is None:
                    last_attack = self.table[-1][0]
                    self.table[-1] = (last_attack, card)
                else:
                    self.table.append((card, None))
            self.table_animations.clear()
            if not self.deal_animation and not self.waiting_for_action and self.turn == 'attack':
                self.waiting_for_action = (not self.attacker.is_bot)
                self.message = f"Ход {self.attacker.name}"

    def check_win(self):
        if len(self.player.hand) == 0:
            self.player_score += 1
            self.coins += 100
            if self.player_score % 5 == 0:
                self.level += 1
            self.game_over = True
            self.winner = self.player
            self.message = f"{self.player.name} выиграл раунд!"
            return True
        if len(self.bot.hand) == 0:
            self.bot_score += 1
            self.game_over = True
            self.winner = self.bot
            self.message = f"{self.bot.name} выиграл раунд!"
            return True
        return False

    def finish_attack(self):
        for attack_card, defense_card in self.table:
            self.discard_pile.append(attack_card)
            if defense_card:
                self.discard_pile.append(defense_card)
        self.table = []
        self.table_animations = []
        self.attacker, self.defender = self.defender, self.attacker
        self.turn = 'attack'
        self.waiting_for_action = False
        self.refill_triggered = True
        self.refill_delay = pygame.time.get_ticks() + 100
        self.message = "Атака завершена (бита)."

    def bot_attack(self):
        if self.attacker.hand:
            card = self.attacker.choose_attack_card(self)
            if card:
                self.attacker.remove_card(card)
                self.animate_card_to_table(card, self.attacker)
                self.message = f"Бот кладёт {card}"
                self.turn = 'defense'
                self.waiting_for_action = (not self.defender.is_bot)
                self.update_card_positions()
            else:
                self.finish_attack()
        else:
            self.message = "Бот не может атаковать (нет карт)."
            self.finish_attack()

    def bot_defense(self):
        if not self.table:
            self.turn = 'attack'
            self.waiting_for_action = (not self.attacker.is_bot)
            return

        last_attack = self.table[-1][0]
        beat_card = self.defender.choose_best_beat(last_attack, self.trump_suit)
        if beat_card:
            self.defender.remove_card(beat_card)
            self.animate_card_to_table(beat_card, self.defender, is_defense=True)
            self.message = f"Бот бьёт {last_attack} картой {beat_card}"
            self.turn = 'attack'
            self.waiting_for_action = False
            self.update_card_positions()
        else:
            for attack_card, _ in self.table:
                self.defender.add_cards([attack_card])
            self.table = []
            self.table_animations = []
            self.message = f"Бот забирает карты (теперь у него {len(self.defender.hand)} карт)."
            self.turn = 'attack'
            self.waiting_for_action = (not self.attacker.is_bot)
            self.message = f"Ход {self.attacker.name}"
            self.update_card_positions()
            self.refill_triggered = True
            self.refill_delay = pygame.time.get_ticks() + 100
            self.check_win()

    def animate_card_to_table(self, card, player, is_defense=False):
        if is_defense:
            idx = len(self.table) - 1 if self.table else 0
            target_x = WIDTH//2 + idx * (CARD_WIDTH + 10) + 40
            target_y = TABLE_Y + 30
        else:
            idx = len(self.table) + len(self.table_animations)
            target_x = WIDTH//2 - (idx) * (CARD_WIDTH + 10) // 2
            target_y = TABLE_Y
        card.set_target(target_x, target_y)
        self.table_animations.append(card)

    def player_attack(self, card):
        # Собираем все ранги на столе (атакующие + защитные + анимированные)
        ranks = []
        for attack, defense in self.table:
            ranks.append(attack.rank)
            if defense:
                ranks.append(defense.rank)
        for c in self.table_animations:
            ranks.append(c.rank)
        ranks = list(set(ranks))
        if ranks and card.rank not in ranks:
            self.message = "Эта карта не подходит."
            return False
        self.attacker.remove_card(card)
        self.animate_card_to_table(card, self.attacker)
        self.message = f"Вы кладёте {card}"
        self.turn = 'defense'
        self.waiting_for_action = (not self.defender.is_bot)
        self.update_card_positions()
        return True

    def player_defense(self, card):
        last_attack = self.table[-1][0]
        if card not in self.defender.can_beat(last_attack, self.trump_suit):
            self.message = "Эта карта не бьёт."
            return False
        self.defender.remove_card(card)
        self.animate_card_to_table(card, self.defender, is_defense=True)
        self.message = f"Вы бьёте {last_attack} картой {card}"
        self.turn = 'attack'
        self.waiting_for_action = False
        self.update_card_positions()
        return True

    def player_take(self):
        for attack_card, _ in self.table:
            self.defender.add_cards([attack_card])
        self.table = []
        self.table_animations = []
        self.message = f"Вы забираете карты (теперь у вас {len(self.defender.hand)} карт)."
        self.turn = 'attack'
        self.waiting_for_action = (not self.attacker.is_bot)
        self.message = f"Ход {self.attacker.name}"
        self.update_card_positions()
        self.refill_triggered = True
        self.refill_delay = pygame.time.get_ticks() + 100
        self.check_win()

    def handle_click(self, pos):
        if self.game_over or self.deal_animation or not self.waiting_for_action:
            return

        # ---- КНОПКА "БИТА" (только когда игрок атакует и на столе есть карты) ----
        if self.turn == 'attack' and self.attacker == self.player and (self.table or self.table_animations):
            bita_rect = pygame.Rect(20, HEIGHT - 70, 120, 50)
            if bita_rect.collidepoint(pos):
                self.finish_attack()
                return

        # ---- КНОПКА "ВЗЯТЬ" (только когда игрок защищается) ----
        if self.turn == 'defense' and self.defender == self.player:
            take_rect = pygame.Rect(WIDTH - 180, HEIGHT - 70, 120, 50)
            if take_rect.collidepoint(pos):
                self.player_take()
                return

        # ---- ВЫБОР КАРТЫ ----
        n = len(self.player.hand)
        if n == 0:
            return
        total_width = n * CARD_WIDTH + (n - 1) * CARD_SPACING
        start_x = (WIDTH - total_width) // 2

        if self.turn == 'attack' and self.attacker == self.player:
            for i, card in enumerate(self.player.hand):
                x = start_x + i * (CARD_WIDTH + CARD_SPACING)
                rect = pygame.Rect(x, HAND_Y_PLAYER, CARD_WIDTH, CARD_HEIGHT)
                if rect.collidepoint(pos):
                    self.player_attack(card)
                    return
        elif self.turn == 'defense' and self.defender == self.player:
            for i, card in enumerate(self.player.hand):
                x = start_x + i * (CARD_WIDTH + CARD_SPACING)
                rect = pygame.Rect(x, HAND_Y_PLAYER, CARD_WIDTH, CARD_HEIGHT)
                if rect.collidepoint(pos):
                    self.player_defense(card)
                    return
        else:
            self.message = "Сейчас не ваш ход."

    def update(self):
        self.update_animation()
        if self.game_over or self.deal_animation:
            return

        if self.refill_triggered and pygame.time.get_ticks() >= self.refill_delay:
            self.refill_triggered = False
            if not self.table and not self.table_animations:
                self.refill_hands()
                self.check_win()

        # Ходы бота
        if not self.table_animations:
            if self.turn == 'attack' and self.attacker.is_bot and not self.bot_thinking:
                self.bot_thinking = True
                self.bot_attack()
                self.bot_thinking = False
            elif self.turn == 'defense' and self.defender.is_bot and not self.bot_thinking:
                self.bot_thinking = True
                self.bot_defense()
                self.bot_thinking = False

        if self.check_win():
            self.message = f"{self.winner.name} выиграл!"

# ---------- ОТРИСОВКА ----------
def draw_card(card, x, y, face_up=True):
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
    if face_up:
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        color = SUIT_COLORS[card.suit]
        rank_text = font_card_rank.render(card.rank, True, color)
        screen.blit(rank_text, (x + 5, y + 5))
        suit_small = font_card_rank.render(card.suit, True, color)
        screen.blit(suit_small, (x + 30, y + 5))
        suit_big = font_card_suit.render(SUIT_SYMBOLS[card.suit], True, color)
        big_rect = suit_big.get_rect(center=(x + CARD_WIDTH//2, y + CARD_HEIGHT//2))
        screen.blit(suit_big, big_rect)
        rank_text2 = font_card_rank.render(card.rank, True, color)
        screen.blit(rank_text2, (x + CARD_WIDTH - 25, y + CARD_HEIGHT - 25))
        suit_small2 = font_card_rank.render(card.suit, True, color)
        screen.blit(suit_small2, (x + CARD_WIDTH - 45, y + CARD_HEIGHT - 25))
    else:
        pygame.draw.rect(screen, (0, 0, 180), rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        for i in range(3):
            for j in range(4):
                pygame.draw.rect(screen, (50, 50, 100), (x + 10 + i*30, y + 10 + j*30, 10, 10))

def draw_game(game, pause_btn_rect, pause_btn_surf, paused):
    screen.fill(GREEN)

    # Козырь
    trump_x = 20
    trump_y = 20
    label = font_trump_label.render("Козырь:", True, WHITE)
    screen.blit(label, (trump_x, trump_y))
    suit_color = SUIT_COLORS[game.trump_suit]
    suit_symbol = SUIT_SYMBOLS[game.trump_suit]
    suit_big = font_card_suit.render(suit_symbol, True, suit_color)
    suit_rect = suit_big.get_rect(topleft=(trump_x, trump_y + 35))
    screen.blit(suit_big, suit_rect)

    # Бита (колода)
    if not game.deck.is_empty():
        deck_x = WIDTH - CARD_WIDTH - 20
        deck_y = (HEIGHT - CARD_HEIGHT) // 2
        pygame.draw.rect(screen, (0, 0, 180), (deck_x, deck_y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(screen, BLACK, (deck_x, deck_y, CARD_WIDTH, CARD_HEIGHT), 2)
        count_font = pygame.font.Font(None, 24)
        count_text = count_font.render(str(len(game.deck.cards)), True, WHITE)
        screen.blit(count_text, (deck_x + CARD_WIDTH//2 - 10, deck_y + CARD_HEIGHT + 10))

    # Стопка сброса (Бита) с названием и красным цветом
    if game.discard_pile:
        discard_x = WIDTH - CARD_WIDTH - 20
        discard_y = DISCARD_Y
        pygame.draw.rect(screen, (180, 0, 0), (discard_x, discard_y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(screen, BLACK, (discard_x, discard_y, CARD_WIDTH, CARD_HEIGHT), 2)
        count_font = pygame.font.Font(None, 24)
        count_text = count_font.render(str(len(game.discard_pile)), True, WHITE)
        screen.blit(count_text, (discard_x + CARD_WIDTH//2 - 10, discard_y + CARD_HEIGHT + 10))
        bita_label = pygame.font.Font(None, 24).render("Бита", True, WHITE)
        screen.blit(bita_label, (discard_x + CARD_WIDTH//2 - 20, discard_y - 20))

    # Карты бота
    n = len(game.bot.hand)
    if n > 0:
        total_width = n * CARD_WIDTH + (n - 1) * CARD_SPACING
        start_x = (WIDTH - total_width) // 2
        for i, card in enumerate(game.bot.hand):
            draw_card(card, start_x + i * (CARD_WIDTH + CARD_SPACING), HAND_Y_BOT, face_up=False)

    # Карты игрока
    n = len(game.player.hand)
    if n > 0:
        total_width = n * CARD_WIDTH + (n - 1) * CARD_SPACING
        start_x = (WIDTH - total_width) // 2
        for i, card in enumerate(game.player.hand):
            draw_card(card, start_x + i * (CARD_WIDTH + CARD_SPACING), HAND_Y_PLAYER, face_up=True)

    # Стол
    table_x = WIDTH // 2 - (len(game.table) * (CARD_WIDTH + 10)) // 2
    for idx, (attack, defense) in enumerate(game.table):
        x = table_x + idx * (CARD_WIDTH + 10)
        draw_card(attack, x, TABLE_Y, face_up=True)
        if defense:
            draw_card(defense, x + 40, TABLE_Y + 30, face_up=True)
        else:
            pygame.draw.rect(screen, RED, (x, TABLE_Y, CARD_WIDTH, CARD_HEIGHT), 3)

    # Анимированные карты
    for card in game.table_animations:
        draw_card(card, card.x, card.y, face_up=True)

    # ---- КНОПКИ ДЛЯ ИГРОКА ----
    if not game.deal_animation and not game.game_over and not game.table_animations and game.waiting_for_action:
        if game.turn == 'defense' and game.defender == game.player:
            take_rect = pygame.Rect(WIDTH - 180, HEIGHT - 70, 120, 50)
            pygame.draw.rect(screen, GRAY, take_rect)
            font = pygame.font.Font(None, 30)
            text = font.render("ВЗЯТЬ", True, BLACK)
            screen.blit(text, (take_rect.x + 20, take_rect.y + 10))

        if game.turn == 'attack' and game.attacker == game.player and (game.table or game.table_animations):
            bita_rect = pygame.Rect(20, HEIGHT - 70, 120, 50)
            pygame.draw.rect(screen, BRIGHT_RED, bita_rect)
            pygame.draw.rect(screen, BLACK, bita_rect, 2)
            font = pygame.font.Font(None, 30)
            text = font.render("БИТА", True, WHITE)
            screen.blit(text, (bita_rect.x + 20, bita_rect.y + 10))

    # Сообщение
    msg_font = pygame.font.Font(None, 28)
    msg = msg_font.render(game.message, True, WHITE)
    screen.blit(msg, (20, HEIGHT - 30))

    # Конец игры
    if game.game_over:
        font = pygame.font.Font(None, 72)
        if game.winner:
            text = font.render(f"{game.winner.name} выиграл раунд!", True, YELLOW)
        else:
            text = font.render("Ничья?", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
        restart = pygame.font.Font(None, 30).render("Нажмите R для следующего раунда", True, WHITE)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 30))

# ---------- ОСНОВНОЙ ЦИКЛ ----------
def main():
    game = Game()
    running = True
    paused = False
    pause_btn_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(pause_btn_surf, (255, 255, 255, 180), (20, 20), 20)
    pygame.draw.circle(pause_btn_surf, (0, 0, 0, 255), (20, 20), 20, 2)
    pygame.draw.line(pause_btn_surf, (0, 0, 0, 255), (12, 10), (12, 30), 4)
    pygame.draw.line(pause_btn_surf, (0, 0, 0, 255), (28, 10), (28, 30), 4)
    pause_btn_rect = pygame.Rect(WIDTH - 60, 10, 40, 40)

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                if event.key == pygame.K_r and game.game_over:
                    game.deck = Deck()
                    game.trump_suit = game.deck.trump_suit
                    game.player.hand = []
                    game.bot.hand = []
                    game.table = []
                    game.table_animations = []
                    game.discard_pile = []
                    game.game_over = False
                    game.winner = None
                    game.message = ""
                    game.start_round()
                    paused = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    if pause_btn_rect.collidepoint(mx, my):
                        paused = not paused
                    elif not paused and not game.game_over:
                        game.handle_click(event.pos)

        if not paused and not game.game_over:
            game.update()

        draw_game(game, pause_btn_rect, pause_btn_surf, paused)

        if paused:
            s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            screen.blit(s, (0, 0))
            pause_font = pygame.font.Font(None, 72)
            pause_text = pause_font.render("ПАУЗА", True, WHITE)
            pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(pause_text, pause_rect)

        screen.blit(pause_btn_surf, (WIDTH - 60, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
