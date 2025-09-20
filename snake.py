import pygame
import sys
import random
from pygame.math import Vector2
import os
import webbrowser  # IMPORTANTE: para abrir links no navegador

# ------------------- Inicialização -------------------
pygame.init()
cell_size = 40
cell_number = 20
screen = pygame.display.set_mode((cell_size*cell_number, cell_size*cell_number))
pygame.display.set_caption("GALME SNAKE")
clock = pygame.time.Clock()

# Fontes
game_font = pygame.font.Font('Font/PoetsenOne-Regular.ttf', 40)
menu_font = pygame.font.Font('Font/PoetsenOne-Regular.ttf', 60)
font_big = pygame.font.SysFont("arialblack", 48)
font_medium = pygame.font.SysFont("arialblack", 36)
font_small = pygame.font.SysFont("arialblack", 28)

# ------------------- Utilitários -------------------
def load_image(path):
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    print(f"Arquivo não encontrado: {path}")
    sys.exit()

def load_sound(path):
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    print(f"Som não encontrado: {path}")
    sys.exit()

def draw_pixel_text(text, font, main_color, border_color, pos):
    text_surface = font.render(text, True, main_color)
    border_surface = font.render(text, True, border_color)
    x, y = pos
    offsets = [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]
    for ox, oy in offsets:
        screen.blit(border_surface, border_surface.get_rect(center=(x+ox, y+oy)))
    screen.blit(text_surface, text_surface.get_rect(center=(x,y)))

def draw_button(text, center, mouse_pos, size="big"):
    if size == "big":
        width, height = 220, 70
        font = font_big
    elif size == "medium":
        width, height = 180, 60
        font = font_medium
    else:  # small
        width, height = 100, 50
        font = font_small

    rect = pygame.Rect(0, 0, width, height)
    rect.center = center

    # sombra
    shadow = rect.copy()
    shadow.x += 4
    shadow.y += 4
    pygame.draw.rect(screen, (50, 80, 100), shadow)

    # botão
    color = (180, 200, 220)
    if rect.collidepoint(mouse_pos):
        color = (255, 220, 100)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (40, 40, 70), rect, 3)

    draw_pixel_text(text, font, (20,20,50), (255,255,255), rect.center)
    return rect

# ------------------- Classes Snake -------------------
class SNAKE:
    def __init__(self, color=(255,255,0)):
        self.body = [Vector2(5,10), Vector2(4,10), Vector2(3,10)]
        self.direction = Vector2(1,0)
        self.new_block = False
        self.color = color

        self.head_up = load_image('Graphics/head_up.png')
        self.head_down = load_image('Graphics/head_down.png')
        self.head_right = load_image('Graphics/head_right.png')
        self.head_left = load_image('Graphics/head_left.png')
        self.tail_up = load_image('Graphics/tail_up.png')
        self.tail_down = load_image('Graphics/tail_down.png')
        self.tail_right = load_image('Graphics/tail_right.png')
        self.tail_left = load_image('Graphics/tail_left.png')
        self.body_vertical = load_image('Graphics/body_vertical.png')
        self.body_horizontal = load_image('Graphics/body_horizontal.png')
        self.body_tr = load_image('Graphics/body_tr.png')
        self.body_tl = load_image('Graphics/body_tl.png')
        self.body_br = load_image('Graphics/body_br.png')
        self.body_bl = load_image('Graphics/body_bl.png')

        self.crunch_sound = load_sound('Sound/crunch.wav')

    def draw_snake(self):
        self.update_head_graphics()
        self.update_tail_graphics()
        for index, block in enumerate(self.body):
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos, y_pos, cell_size, cell_size)

            if index == 0:
                screen.blit(self.head, block_rect)
            elif index == len(self.body)-1:
                screen.blit(self.tail, block_rect)
            else:
                prev_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block
                if prev_block.x == next_block.x:
                    screen.blit(self.body_vertical, block_rect)
                elif prev_block.y == next_block.y:
                    screen.blit(self.body_horizontal, block_rect)
                else:
                    if (prev_block.x == -1 and next_block.y == -1) or (prev_block.y == -1 and next_block.x == -1):
                        screen.blit(self.body_tl, block_rect)
                    elif (prev_block.x == -1 and next_block.y == 1) or (prev_block.y == 1 and next_block.x == -1):
                        screen.blit(self.body_bl, block_rect)
                    elif (prev_block.x == 1 and next_block.y == -1) or (prev_block.y == -1 and next_block.x == 1):
                        screen.blit(self.body_tr, block_rect)
                    elif (prev_block.x == 1 and next_block.y == 1) or (prev_block.y == 1 and next_block.x == 1):
                        screen.blit(self.body_br, block_rect)

    def update_head_graphics(self):
        head_relation = self.body[1] - self.body[0]
        if head_relation == Vector2(1,0): self.head = self.head_left
        elif head_relation == Vector2(-1,0): self.head = self.head_right
        elif head_relation == Vector2(0,1): self.head = self.head_up
        elif head_relation == Vector2(0,-1): self.head = self.head_down

    def update_tail_graphics(self):
        tail_relation = self.body[-2] - self.body[-1]
        if tail_relation == Vector2(1,0): self.tail = self.tail_left
        elif tail_relation == Vector2(-1,0): self.tail = self.tail_right
        elif tail_relation == Vector2(0,1): self.tail = self.tail_up
        elif tail_relation == Vector2(0,-1): self.tail = self.tail_down

    def move_snake(self):
        body_copy = self.body[:]
        body_copy.insert(0, body_copy[0] + self.direction)
        if not self.new_block:
            body_copy.pop()
        self.body = body_copy
        self.new_block = False

    def add_block(self):
        self.new_block = True

    def play_crunch_sound(self):
        self.crunch_sound.play()

class FRUIT:
    def __init__(self):
        self.randomize()
    def draw_fruit(self):
        fruit_rect = pygame.Rect(int(self.pos.x*cell_size), int(self.pos.y*cell_size), cell_size, cell_size)
        screen.blit(apple, fruit_rect)
    def randomize(self):
        self.pos = Vector2(random.randint(0, cell_number-1), random.randint(0, cell_number-1))

class MAIN:
    def __init__(self, snake_color=(255,255,0), bg_color=(167,209,61)):
        self.snake = SNAKE(snake_color)
        self.fruit = FRUIT()
        self.bg_color = bg_color
    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()
    def draw_elements(self):
        self.draw_grass()
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()
    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()
        for block in self.snake.body[1:]:
            if block == self.fruit.pos:
                self.fruit.randomize()
    def check_fail(self):
        global game_state
        if not 0 <= self.snake.body[0].x < cell_number or not 0 <= self.snake.body[0].y < cell_number:
            game_state = "game_over"
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                game_state = "game_over"
    def draw_grass(self):
        dark_grass = (max(0,self.bg_color[0]-30), max(0,self.bg_color[1]-30), max(0,self.bg_color[2]-30))
        for row in range(cell_number):
            for col in range(cell_number):
                color = self.bg_color if (row+col)%2==0 else dark_grass
                rect = pygame.Rect(col*cell_size,row*cell_size,cell_size,cell_size)
                pygame.draw.rect(screen,color,rect)
    def draw_score(self):
        score = str(len(self.snake.body)-3)
        score_surface = game_font.render(score,True,(56,47,12))
        x = cell_size*cell_number - 60
        y = cell_size*cell_number - 40
        screen.blit(score_surface,score_surface.get_rect(center=(x,y)))
        screen.blit(apple,apple.get_rect(midright=(x-20,y)))

# ------------------- Recursos -------------------
apple = load_image('Graphics/apple.png')
snake_color = (255,255,0)
bg_color = (167,209,61)
speed = 150
SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE,speed)

main_game = MAIN(snake_color,bg_color)
game_state = "menu"

def reset_game():
    global main_game
    main_game = MAIN(snake_color,bg_color)
    pygame.time.set_timer(SCREEN_UPDATE,speed)

# ------------------- Loop principal -------------------
while True:
    mouse_pos = pygame.mouse.get_pos()
    screen.fill((100,200,100))

    # --- Menu ---
    if game_state == "menu":
        draw_pixel_text("GALME SNAKE", menu_font, (255,255,0), (0,0,0), (cell_size*cell_number//2, 80))
        draw_pixel_text("MENU PRINCIPAL", game_font, (255,150,0), (0,0,0), (cell_size*cell_number//2, 140))
        play_btn = draw_button("PLAY", (cell_size*cell_number//2, 220), mouse_pos, size="medium")
        pause_btn = draw_button("PAUSE", (cell_size*cell_number//2, 320), mouse_pos, size="medium")
        options_btn = draw_button("OPTIONS", (cell_size*cell_number//2, 420), mouse_pos, size="medium")
        home_btn = draw_button("HOME", (250, 520), mouse_pos, size="small")
        info_btn = draw_button("INFO", (400, 520), mouse_pos, size="small")
        share_btn = draw_button("SHARE", (550, 520), mouse_pos, size="small")

    elif game_state == "options":
        draw_pixel_text("CENTRAL DE AJUDA", font_big, (255,255,255), (0,0,0), (400, 200))
        draw_pixel_text("Desenvolvido por Mufe", font_small, (255,200,0), (0,0,0), (400, 260))
        back_btn = draw_button("VOLTAR", (400, 400), mouse_pos, size="medium")

    elif game_state == "playing":
        main_game.draw_elements()

    elif game_state == "paused":
        draw_pixel_text("PAUSADO", font_big, (255,0,0), (0,0,0), (400, 300))

    elif game_state == "game_over":
        overlay = pygame.Surface(screen.get_size(),pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        screen.blit(overlay,(0,0))
        draw_pixel_text("VOCÊ MORREU!", menu_font, (255,0,0), (0,0,0), (cell_size*cell_number//2, cell_size*cell_number//2-100))
        draw_pixel_text("ENTER - Jogar Novamente", game_font, (255,255,255), (0,0,0), (cell_size*cell_number//2, cell_size*cell_number//2-20))
        draw_pixel_text("ESC - Sair", game_font, (255,255,255), (0,0,0), (cell_size*cell_number//2, cell_size*cell_number//2+40))

    # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "menu":
                if play_btn.collidepoint(mouse_pos):
                    reset_game()
                    game_state = "playing"
                elif pause_btn.collidepoint(mouse_pos):
                    game_state = "paused"
                elif options_btn.collidepoint(mouse_pos):
                    game_state = "options"
                elif home_btn.collidepoint(mouse_pos):
                    print("HOME clicado")
                elif info_btn.collidepoint(mouse_pos):
                    print("INFO clicado")
                elif share_btn.collidepoint(mouse_pos):
                    # ABRIR LINK NO NAVEGADOR
                    webbrowser.open("https://GalmeSnake.com")
            elif game_state == "options":
                if back_btn.collidepoint(mouse_pos):
                    game_state = "menu"

        if event.type == SCREEN_UPDATE and game_state == "playing":
            main_game.update()

        if event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if event.key == pygame.K_w and main_game.snake.direction.y != 1:
                    main_game.snake.direction = Vector2(0,-1)
                if event.key == pygame.K_s and main_game.snake.direction.y != -1:
                    main_game.snake.direction = Vector2(0,1)
                if event.key == pygame.K_a and main_game.snake.direction.x != 1:
                    main_game.snake.direction = Vector2(-1,0)
                if event.key == pygame.K_d and main_game.snake.direction.x != -1:
                    main_game.snake.direction = Vector2(1,0)
            if game_state == "game_over":
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = "playing"
            if event.key == pygame.K_ESCAPE:
                if game_state in ["playing","paused","game_over"]:
                    game_state = "menu"
                elif game_state == "menu":
                    pygame.quit(); sys.exit()

    pygame.display.update()
    clock.tick(60)
