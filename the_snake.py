from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_GRID = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# ВСЕ возможные позиции яблока — сразу в пиксельных координатах
ALL_CELLS: set[tuple[int, int]] = {
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
TEXT_COLOR = (30, 30, 30)

# Скорость движения змейки:
SPEED = 10

pg.init()
# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
# Настройка времени:
clock = pg.time.Clock()
# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

font = pg.font.SysFont('Arial', 28, bold=True)


# Все классы игры.
class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: tuple[int, int] | None = None,
        body_color: tuple[int, int, int] | None = None
    ) -> None:
        self.position = position
        if (
            body_color is None
            or not isinstance(body_color, (tuple, list))
            or len(body_color) < 3
        ):
            self.body_color = (200, 200, 200)
        else:
            self.body_color = tuple(body_color)

    @staticmethod
    def draw_empty_cell(pos: tuple[int, int]) -> None:
        """Рисует пустую клетку: только цвет фона, БЕЗ рамки."""
        x, y = pos
        rect = pg.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
        # Рамка не рисуется — клетка полностью закрашена фоном

    def draw_single_cell(
        self,
        pos: tuple[int, int] | None,
        color: tuple[int, int, int] | None = None
    ) -> None:
        """Отрисовывает одну ячейку (квадрат) на экране."""
        x, y = pos
        rect = pg.Rect(x, y, GRID_SIZE, GRID_SIZE)
        final_color = color if color is not None else self.body_color
        pg.draw.rect(screen, final_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Базовый метод отрисовки объекта."""
        raise NotImplementedError(
            f'Метод draw() не реализован в классе {type(self)}.'
            'Реализуйте его в наследнике для корректной отрисовки.'
        )


class Apple(GameObject):
    """Класс, отвечающий за объект - яблоко."""

    def __init__(
        self,
        body_color: tuple[int, int, int] = APPLE_COLOR,
        snake_positions: list[tuple[int, int]] | None = None
    ) -> None:
        super().__init__(body_color=body_color)
        self.randomize_position(snake_positions or [])

    def randomize_position(
        self,
        snake_positions: list[tuple[int, int]]
    ) -> None:
        """Устанавливает случайную позицию яблока, выровненную по сетке."""
        occupied_positions: set[tuple[int, int]] = set(snake_positions)
        self.position = choice(tuple(ALL_CELLS - occupied_positions))

    # Метод draw класса Apple
    def draw(self):
        """Рисует яблоко на экране."""
        self.draw_single_cell(self.position)


class Snake(GameObject):
    """Класс, отвечающий за объект - змейка."""

    def __init__(self, body_color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        super().__init__(body_color=body_color)
        self.reset()

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки (первый элемент списка)."""
        return self.positions[0]

    def update_direction(self, new_direction: tuple[int, int]) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if new_direction != OPPOSITE.get(self.direction):
            self.direction = new_direction

    def move(self) -> None:
        """Вычисляет новую позицию головы и обновляет список."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        self.positions.insert(0, (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        ))
        # Если змейка не выросла, удаляем хвост
        if len(self.positions) > self.length:
            self.positions.pop()

    def check_self_collision(self) -> bool:
        """Проверяем не врезалась ли змея сама в себя."""
        return self.get_head_position() in self.positions[4:]

    def reset(self) -> None:
        """Сброс змеи в начальное состояние."""
        self.length = 1
        self.positions = [CENTER_GRID]
        self.direction = RIGHT

    # Метод draw класса Snake
    def draw(self) -> None:
        """Полная отрисовка змейки."""
        for pos in self.positions:
            self.draw_single_cell(pos)

    def draw_partial(
        self,
        tail_to_erase: tuple[int, int] | None,
        head_to_draw: tuple[int, int] | None
    ) -> None:
        """Отрисовывает голову и кончик хвоста змейки."""
        if tail_to_erase is not None:
            GameObject.draw_empty_cell(tail_to_erase)
        if head_to_draw is not None:
            self.draw_single_cell(head_to_draw, self.body_color)


def handle_keys(snake):
    """Функция обработки действий пользователя с клавиатуры."""
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            new_direction = VALID_TURNS.get((snake.direction, event.key))
            if new_direction is not None:
                snake.update_direction(new_direction)


def main():
    """
    Главная функция игры: инициализация объектов: яблоко и змейка,
    игровой процесс,
    завершение.
    """
    # Экземпляры классов.
    snake = Snake()
    apple = Apple(snake_positions=snake.positions)
    # Максимальная длина змейки:
    max_length = 1

    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    apple.draw()
    pg.display.update()

    while True:
        handle_keys(snake)

        last_tail: tuple[int, int] | None = None
        if len(snake.positions) == snake.length:
            last_tail = snake.positions[-1]

        snake.move()
        new_head = snake.get_head_position()

        # Проверка столкновения с собой
        if snake.check_self_collision():
            if snake.length > max_length:
                max_length = snake.length
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.draw()
            apple.draw()
            pg.display.update()
            continue

        if new_head == apple.position:
            snake.length += 1
            if snake.length > max_length:
                max_length = snake.length
            apple.randomize_position(snake.positions)

        snake.draw_partial(
            tail_to_erase=last_tail,
            head_to_draw=new_head
        )
        apple.draw()

        caption = (
            f'Змейка | Длина: {snake.length} | '
            f'Рекорд: {max_length} | Выход: ESCAPE'
        )
        pg.display.set_caption(caption)
        pg.display.update()
        clock.tick(SPEED)
    pg.quit()


if __name__ == '__main__':
    main()
