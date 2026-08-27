from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_GRID = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# ВСЕ возможные позиции яблока — сразу в пиксельных координатах
ALL_GRIDS: set[tuple[int, int]] = {
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

font = pg.font.SysFont('Arial', 24, bold=True)


# Все классы игры.
class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: tuple[int, int] | None = None,
        body_color: tuple[int, int, int] | None = None
    ) -> None:
        self.position = position
        self.body_color = body_color if body_color else (200, 200, 200)

    def draw_single_cell(
        self,
        pos: tuple[int, int],
        color: tuple[int, int, int] | None = None
    ) -> None:
        """Отрисовывает одну ячейку (квадрат) на экране."""
        x, y = pos
        rect = pg.Rect(x, y, GRID_SIZE, GRID_SIZE)
        final_color = color or self.body_color
        pg.draw.rect(screen, final_color, rect)

    def draw(self):
        """Базовый метод отрисовки объекта."""
        obj_type = type(self)
        raise NotImplementedError(
            f'Метод draw() не реализован в классе {obj_type}.'
        )


class Apple(GameObject):
    """Класс, отвечающий за объект - яблоко."""

    def __init__(
        self,
        body_color: tuple[int, int, int] = APPLE_COLOR,
        occupied_positions: list[tuple[int, int]] | None = None
    ) -> None:
        start_pos = self.randomize_position(occupied_positions or [])
        super().__init__(position=start_pos, body_color=body_color)

    def randomize_position(
        self,
        occupied: list[tuple[int, int]]
    ) -> tuple[int, int]:
        """Устанавливает случайную позицию яблока, выровненную по сетке."""
        self.position = choice(tuple(ALL_GRIDS - set(occupied)))
        return self.position

    # Метод draw класса Apple
    def draw(self) -> None:
        """Рисует яблоко на экране."""
        self.draw_single_cell(self.position)


class Snake(GameObject):
    """Класс, отвечающий за объект - змейка."""

    def __init__(self, body_color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        super().__init__(position=CENTER_GRID, body_color=body_color)
        self.reset()

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки (первый элемент списка)."""
        return self.positions[0]

    def update_direction(self, new_direction: tuple[int, int]) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if new_direction != OPPOSITE.get(self.direction):
            self.direction = new_direction

    def move(self) -> tuple[tuple[int, int] | None, tuple[int, int]]:
        """Вычисляет новую позицию головы и обновляет список."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        last_tail = None
        # Если змейка не выросла, удаляем хвост
        if len(self.positions) == self.length:
            last_tail = self.positions[-1]
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        return last_tail, new_head

    def check_self_collision(self) -> bool:
        """Проверяем не врезалась ли змея сама в себя."""
        return self.get_head_position() in self.positions[4:]

    def reset(self) -> None:
        """Сброс змеи в начальное состояние."""
        self.length = 1
        self.positions = [CENTER_GRID]
        self.direction = RIGHT
        self.position = CENTER_GRID


def handle_keys(snake) -> None:
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


def main() -> None:
    """
    Главная функция игры: инициализация объектов: яблоко и змейка,
    игровой процесс,
    завершение.
    """
    # Экземпляры классов.
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)
    # Максимальная длина змейки:
    max_length = 1

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        handle_keys(snake)
        current_tail_pos = (
            snake.positions[-1]
            if len(snake.positions) > 1
            else None
        )
        last_tail, new_head = snake.move()
        ate_apple = False

        # Проверка столкновения с собой
        if snake.check_self_collision():
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
            continue
        elif new_head == apple.position:
            snake.length += 1
            ate_apple = True
            screen.fill(BOARD_BACKGROUND_COLOR)
            if snake.length > max_length:
                max_length = snake.length
            apple.randomize_position(snake.positions)
        if not ate_apple:
            if last_tail is not None:
                snake.draw_single_cell(last_tail, BOARD_BACKGROUND_COLOR)
        else:
            if current_tail_pos is not None:
                snake.draw_single_cell(
                    current_tail_pos, BOARD_BACKGROUND_COLOR
                )
        snake.draw_single_cell(new_head, SNAKE_COLOR)
        apple.draw()

        caption = (
            f'Змейка | Длина: {snake.length} | '
            f'Рекорд: {max_length} | Выход: ESCAPE'
        )
        pg.display.set_caption(caption)
        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
