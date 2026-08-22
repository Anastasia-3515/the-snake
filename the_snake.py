import pygame as pg
from random import choice

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_FIELD = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# ВСЕ возможные позиции яблока — сразу в пиксельных координатах
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

VALID_TURNS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,

    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,

    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,

    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

BOARD_BACKGROUND_COLOR = (211, 211, 211)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

pg.init()
# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')
# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=None, body_color=None):
        self.position = position
        self.body_color = body_color

    @staticmethod
    def draw_cells(screen, positions, color=None):
        """Отрисовывает одну ячейку (квадрат) на экране."""
        for pos in positions:
            if pos is None:
                continue
            x, y = pos
            rect = pg.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self, screen):
        """Базовый метод отрисовки объекта."""
        raise NotImplementedError(
            f'Метод draw() не реализован в классе {self.__class__.__name__}.'
            'Реализуйте его в наследнике для корректной отрисовки.'
        )


class Apple(GameObject):
    """Класс, отвечающий за объект - яблоко."""

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color=body_color)
        self.randomize_position([])

    def randomize_position(self, occupied_positions):
        """Устанавливает случайную позицию яблока, выровненную по сетке."""
        self.position = choice(tuple(ALL_CELLS - set(occupied_positions)))

    # Метод draw класса Apple
    def draw(self, screen):
        """Рисует яблоко на экране."""
        GameObject.draw_cells(screen, [self.position], self.body_color)


class Snake(GameObject):
    """Класс, отвечающий за объект - змейка."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color=body_color)

        self.reset()

    def get_head_position(self):
        """Возвращает позицию головы змейки (первый элемент списка)."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Метод обновления направления после нажатия на кнопку."""
        if new_direction == OPPOSITE.get(self.direction):
            return
        self.direction = new_direction

    def move(self):
        """Вычисляет новую позицию головы и обновляет список."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        self.positions.insert(
            0,
            ((head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
             (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT)
        )
        # Если змейка не выросла, удаляем хвост
        if len(self.positions) > self.length:
            self.positions.pop()

    def check_self_collision(self):
        """Проверяем не врезалась ли змея сама в себя."""
        return self.get_head_position() in self.positions[2:]

    def reset(self):
        """Сброс змеи в начальное состояние."""
        self.length = 1
        self.positions = [CENTER_FIELD]
        self.direction = RIGHT

    # Метод draw класса Snake
    def draw(self, screen):
        """Отрисовывает голову и кончик хвоста змейки."""
        if not self.positions:
            return
        GameObject.draw_cells(screen, self.positions, self.body_color)


def handle_keys(snake):
    """Функция обработки действий пользователя с клавиатуры."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit
            new_direction = VALID_TURNS.get((snake.direction, event.key))
            if new_direction is not None:
                snake.update_direction(new_direction)
    return True


def main():
    """
    Главная функция игры: инициализация объектов: яблоко и змейка,
    игровой процесс,
    завершение.
    """
    # Экземпляры классов.
    snake = Snake()
    apple = Apple()
    # Максимальная длина змейки:
    max_length = 1

    running = True
    while running:
        running = handle_keys(snake)
        if not running:
            break

        # Очистка экрана перед новой отрисовкой
        screen.fill(BOARD_BACKGROUND_COLOR)

        snake.move()

        # Проверка столкновения с собой
        if snake.check_self_collision():
            if snake.length > max_length:
                max_length = snake.length
            snake.reset()
            apple.randomize_position(snake.positions)
            continue

        # Проверка поедания яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            if snake.length > max_length:
                max_length = snake.length
            apple.randomize_position(snake.positions)

        apple.draw(screen)
        snake.draw(screen)

        pg.display.update()
        clock.tick(SPEED)

        # Формируем заголовок с динамической информацией
        useful_information = (
            f'Змейка | Длина: {snake.length} | Рекорд: {max_length}'
            f'| Скорость: {SPEED} FPS | Выход: закрыть окно или  ESCAPE'
        )
        pg.display.set_caption(useful_information)

    pg.quit()


if __name__ == '__main__':
    main()
