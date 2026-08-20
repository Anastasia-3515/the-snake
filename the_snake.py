from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=None, body_color=None):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на экране."""
        pass


class Apple(GameObject):
    """Класс, отвечающий за объект - яблоко."""

    def __init__(self, snake_positions=None, body_color=APPLE_COLOR):
        if snake_positions is None:
            snake_positions = []
        super().__init__(position=(0, 0), body_color=body_color)
        self.snake_positions = snake_positions
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайную позицию яблока, выровненную по сетке."""
        while True:
            max_x = (SCREEN_WIDTH // GRID_SIZE) - 1
            max_y = (SCREEN_HEIGHT // GRID_SIZE) - 1

            x = randint(0, max_x) * GRID_SIZE
            y = randint(0, max_y) * GRID_SIZE

            self.position = (x, y)
            if self.position not in self.snake_positions:
                self.position = self.position
                break

    # Метод draw класса Apple
    def draw(self):
        """Рисует яблоко на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, отвечающий за объект - змейка."""

    def __init__(self, position=None, direction=RIGHT):
        super().__init__(position, body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [position]
        self.direction = direction
        self.next_direction = None

    def get_head_position(self):
        """Возвращает позицию головы змейки (первый элемент списка)."""
        return self.positions[0]

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
        self.next_direction = None

    def move(self):
        """Вычисляет новую позицию головы и обновляет список."""
        current_head_position = self.get_head_position()
        dx, dy = self.direction
        new_head_position = (
            (current_head_position[0] + dx * GRID_SIZE) % SCREEN_WIDTH,
            (current_head_position[1] + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head_position)
        # Если змейка не выросла, удаляем хвост
        if len(self.positions) > self.length:
            return self.positions.pop()

    def check_self_collision(self):
        """Проверяем не врезалась ли змея сама в себя."""
        return self.get_head_position() in self.positions[1:]

    def reset(self):
        """Сброс змеи в начальное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None

    # Метод draw класса Snake
    def draw(self):
        """Отрисовывает все сегменты змейки на экране."""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """Функция обработки действий пользователя с клавиатуры."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Главная функция игры: инициализация объектов: яблоко и змейка,
    игровой процесс,
    завершение.
    """
    pygame.init()

    # Экземпляры классов.
    snake = Snake((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    apple = Apple(snake.positions)

    while True:
        handle_keys(snake)
        snake.update_direction()

        # Очистка экрана перед новой отрисовкой
        screen.fill(BOARD_BACKGROUND_COLOR)

        snake.move()

        # Проверка столкновения с собой
        if snake.check_self_collision():
            snake.reset()
            apple.snake_positions = snake.positions
            apple.randomize_position()
            continue

        # Проверка поедания яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        apple.draw()
        snake.draw()

        pygame.display.update()
        clock.tick(SPEED)

    pygame.quit()


if __name__ == '__main__':
    main()
