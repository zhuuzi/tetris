import pygame
from copy import deepcopy
from random import choice, randrange
from pygame import mixer

# Game constants
W, H = 10, 20  # Width and height of the game grid
TILE = 45  # Size of each tile
GAME_RES = W * TILE, H * TILE  # Resolution of the game surface
RES = 750, 940  # Overall screen resolution
FPS = 60  # Frames per second
BG_COLOR = (40, 40, 40)  # Background color

# Pygame initialization
pygame.init()
sc = pygame.display.set_mode(RES)  # Main screen
game_sc = pygame.Surface(GAME_RES)  # Game surface
clock = pygame.time.Clock()  # Game clock

# Grid initialization
grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

# Tetris figures and their positions
figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

# Create figure objects based on positions
figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)  # Rect for drawing figures
field = [[0 for i in range(W)] for j in range(H)]  # Game field to store placed figures

anim_count, anim_speed, anim_limit = 0, 60, 2000  # Animation variables

game_bg = pygame.image.load('img/bg2.jpg').convert()  # Background image

# Font and text objects
main_font = pygame.font.Font('font/font.ttf', 65)
font = pygame.font.Font('font/font.ttf', 45)
title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_score = font.render('score:', True, pygame.Color('green'))
title_record = font.render('record:', True, pygame.Color('purple'))

# Function to generate random colors
get_color = lambda: (randrange(30, 256), randrange(30, 256), randrange(30, 256))

# Initialize current and next figures, as well as their colors
figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0  # Initial score and lines cleared
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

# Function to check if the current figure is
# within the borders and not colliding with other placed figures
def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True

# Function to retrieve the current record from a file
def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')

# Function to set the record in a file
def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))

# Game loop
while True:
    record = get_record()
    dx, rotate = 0, False
    sc.fill(color=BG_COLOR)
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))

    # Initialize the mixer for sound effects
    mixer.init()
    mixer.music.load('sound/Lineclear.wav')
    mixer.music.set_volume(0.7)

    # Delay for full lines
    for i in range(lines):
        mixer.music.play()
        pygame.time.wait(600)

    # Event handling and controls
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
    # Move the current figure horizontally
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break

    # Move the current figure vertically
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            mixer.init()
            mixer.music.load('sound/Drop.wav')
            mixer.music.set_volume(0.7)
            mixer.music.play()
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break
    # Rotate the current figure
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break

    # Check for completed lines
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += 3
            lines += 1
    # Update the score
    score += scores[lines]
    # Draw the grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
    # Draw the current figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)
    # Draw the filled cells in the grid
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    # Draw the next figure preview
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)

    # Draw the titles
    sc.blit(title_tetris, (485, 10))
    sc.blit(title_score, (535, 780))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (550, 840))
    sc.blit(title_record, (525, 650))
    sc.blit(font.render(record, True, pygame.Color('gold')), (550, 710))

    # Game over condition
    for i in range(W):
        if field[0][i]:
            mixer.init()
            mixer.music.load('sound/Gameover.wav')
            mixer.music.set_volume(0.7)
            mixer.music.play()
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)
            mixer.music.stop()

    pygame.display.flip()
    clock.tick(FPS)
