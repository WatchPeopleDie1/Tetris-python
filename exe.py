import pygame, sys, random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("tetris")

BLACK = (0, 0, 0)
GRAY = (40, 40, 40)

COLS, ROWS = 10, 20
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = COLS * BLOCK_SIZE, ROWS * BLOCK_SIZE
GRID_X = (WIDTH - GRID_WIDTH) // 2
GRID_Y = (HEIGHT - GRID_HEIGHT) // 2

SHAPES = {
    'I': [(0, 1), (1, 1), (2, 1), (3, 1)],
    'J': [(0, 0), (0, 1), (1, 1), (2, 1)],
    'L': [(2, 0), (0, 1), (1, 1), (2, 1)],
    'O': [(1, 0), (2, 0), (1, 1), (2, 1)],
    'S': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'T': [(1, 0), (0, 1), (1, 1), (2, 1)],
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)]
}

class Shape:
    def __init__(self, shape_key, color, position):
        self.shape = SHAPES[shape_key]
        self.color = color
        self.position = position  # (x, y)

    def draw_shape(self, surface, offset_x, offset_y, block_size):
        for x, y in self.shape:
            rect = pygame.Rect(
                offset_x + (self.position[0] + x) * block_size,
                offset_y + (self.position[1] + y) * block_size,
                block_size,
                block_size
            )
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, (40, 40, 40), rect, 2)
            
    
    def default_moves(self):
        self.position = (self.position[0], self.position[1] + 1)

    def move_left(self, grid):
        if not check_collision(self, grid, dx=-1):
            self.position = (self.position[0] - 1, self.position[1])

    def move_right(self, grid):
        if not check_collision(self, grid, dx=1):
            self.position = (self.position[0] + 1, self.position[1])

    def move_down(self, grid):
        if not check_collision(self, grid, dy=1):
            self.position = (self.position[0], self.position[1] + 1)

    def rotate_right(self, grid):
        new_shape = [(y, -x) for x, y in self.shape]
        temp = self.shape
        self.shape = new_shape
        if check_collision(self, grid):
            self.shape = temp  # revert if collides

    def rotate_left(self, grid):
        new_shape = [(-y, x) for x, y in self.shape]
        temp = self.shape
        self.shape = new_shape
        if check_collision(self, grid):
            self.shape = temp


def draw_grid(surface):
    border_rect = pygame.Rect(GRID_X, GRID_Y, GRID_WIDTH, GRID_HEIGHT)
    pygame.draw.rect(surface, (200, 200, 200), border_rect, 3)
    for x in range(COLS + 1):
        pygame.draw.line(surface, GRAY,
                         (GRID_X + x * BLOCK_SIZE, GRID_Y),
                         (GRID_X + x * BLOCK_SIZE, GRID_Y + GRID_HEIGHT))
    for y in range(ROWS + 1):
        pygame.draw.line(surface, GRAY,
                         (GRID_X, GRID_Y + y * BLOCK_SIZE),
                         (GRID_X + GRID_WIDTH, GRID_Y + y * BLOCK_SIZE))
        
def check_collision(shape, grid, dx=0, dy=0):
    for x, y in shape.shape:
        grid_x = shape.position[0] + x + dx
        grid_y = shape.position[1] + y + dy
        if grid_x < 0 or grid_x >= COLS or grid_y >= ROWS:
            return True
        if grid_y >= 0 and grid[grid_y][grid_x] is not None:
            return True
    return False
def clear_rows(grid):
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    cleared = ROWS - len(new_grid)
    for _ in range(cleared):
        new_grid.insert(0, [None for _ in range(COLS)])
    return new_grid

clock = pygame.time.Clock()
running = True

clock = pygame.time.Clock()
running = True

gravity_timer = 0
gravity_speed = 60  # lower = faster fall

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
random_shape_key = random.choice(list(SHAPES.keys()))
player_shape = Shape(random_shape_key, random.choice(colors), (3, 0))
grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
# spawn new piece

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_shape.move_left(grid)
            elif event.key == pygame.K_RIGHT:
                player_shape.move_right(grid)
            elif event.key == pygame.K_DOWN:
                player_shape.move_down(grid)
            elif event.key == pygame.K_SPACE:
                while not check_collision(player_shape, grid, dy=1):
                    player_shape.default_moves()
            if event.key == pygame.K_z:
                player_shape.rotate_right(grid)
            elif event.key == pygame.K_UP:
                player_shape.rotate_left(grid)

    gravity_timer += 1
    if gravity_timer >= gravity_speed:
        gravity_timer = 0
        if not check_collision(player_shape, grid, dy=1):
            player_shape.default_moves()
        else:
            # lock piece
            for x, y in player_shape.shape:
                grid_x = player_shape.position[0] + x
                grid_y = player_shape.position[1] + y
                if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                    grid[grid_y][grid_x] = player_shape.color

            # clear rows
            grid = clear_rows(grid)

            # spawn new piece
            random_shape_key = random.choice(list(SHAPES.keys()))
            player_shape = Shape(random_shape_key, random.choice(colors), (3, 0))

            # check game over
            if check_collision(player_shape, grid):
                running = False
                print("Game Over!")

    # draw everything AFTER updating the grid and piece
    screen.fill(BLACK)
    draw_grid(screen)

    # draw locked pieces
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            if color:
                rect = pygame.Rect(
                    GRID_X + x * BLOCK_SIZE,
                    GRID_Y + y * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRAY, rect, 2)

    # draw the falling piece
    player_shape.draw_shape(screen, GRID_X, GRID_Y, BLOCK_SIZE)

                        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
