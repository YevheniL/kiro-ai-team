import pygame
import random

pygame.init()

# Constants
COLS, ROWS = 10, 20
CELL = 30
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL
FPS = 60

# Colors
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0),    # Z
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
]


def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]


def valid(board, shape, ox, oy):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                nx, ny = ox + x, oy + y
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and board[ny][nx]:
                    return False
    return True


def lock(board, shape, ox, oy, color):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell and oy + y >= 0:
                board[oy + y][ox + x] = color


def clear_lines(board):
    cleared = 0
    new_board = [row for row in board if any(c == 0 for c in row)]
    cleared = ROWS - len(new_board)
    return [[0] * COLS for _ in range(cleared)] + new_board, cleared


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28)

    board = [[0] * COLS for _ in range(ROWS)]
    score = 0

    def new_piece():
        idx = random.randint(0, 6)
        return SHAPES[idx], COLORS[idx], COLS // 2 - len(SHAPES[idx][0]) // 2, 0

    shape, color, px, py = new_piece()
    drop_timer = 0
    drop_interval = 500  # ms
    game_over = False

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_LEFT and valid(board, shape, px - 1, py):
                    px -= 1
                elif event.key == pygame.K_RIGHT and valid(board, shape, px + 1, py):
                    px += 1
                elif event.key == pygame.K_DOWN and valid(board, shape, px, py + 1):
                    py += 1
                elif event.key == pygame.K_UP:
                    rotated = rotate(shape)
                    if valid(board, rotated, px, py):
                        shape = rotated
                elif event.key == pygame.K_SPACE:
                    while valid(board, shape, px, py + 1):
                        py += 1
            if event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_r:
                board = [[0] * COLS for _ in range(ROWS)]
                score = 0
                shape, color, px, py = new_piece()
                game_over = False

        if not game_over:
            drop_timer += dt
            if drop_timer >= drop_interval:
                drop_timer = 0
                if valid(board, shape, px, py + 1):
                    py += 1
                else:
                    lock(board, shape, px, py, color)
                    board, cleared = clear_lines(board)
                    score += [0, 100, 300, 500, 800][cleared]
                    shape, color, px, py = new_piece()
                    if not valid(board, shape, px, py):
                        game_over = True

        # Draw
        screen.fill(BLACK)
        # Grid
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
                if board[y][x]:
                    pygame.draw.rect(screen, board[y][x], rect)
                pygame.draw.rect(screen, GRAY, rect, 1)
        # Current piece
        if not game_over:
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell and py + y >= 0:
                        rect = pygame.Rect((px + x) * CELL, (py + y) * CELL, CELL, CELL)
                        pygame.draw.rect(screen, color, rect)
                        pygame.draw.rect(screen, GRAY, rect, 1)
        # Score
        txt = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(txt, (5, 5))
        if game_over:
            go_txt = font.render("GAME OVER (R)", True, (255, 50, 50))
            screen.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()


if __name__ == "__main__":
    main()
