import string
from random import choice
BOARD_SIZE = 6  # Размер поля
FLEET_COMPOSITION = {3: 1, 2: 2, 1: 4}  # Состав флотов (количество палуб: количество кораблей)


def print_separator(n):
    """Функция выводит разделитель длины n"""
    for i in range(n):
        print('_', end='')
    print()


class Point:
    """Класс клетки игрового поля"""

    __owning_ship = None  # Корабль-"хозяин" клетки (по умолчанию нет)

    def __init__(self, x, y, condition='O', neighbours=0):
        """Конструктор класса"""
        self.__x = x  # Координата x
        self.__y = y  # Координата y
        self.__condition = condition  # Состояние клетки
        self.__neighbours = neighbours  # Количество кораблей рядом или на клетке

    @property
    def x(self):
        """Геттер координаты x"""
        return self.__x

    @property
    def y(self):
        """Геттер координаты y"""
        return self.__y

    @property
    def condition(self):
        """Геттер состояния клетки"""
        return self.__condition

    @property
    def shootable(self):
        """Геттер возможности обстрела клетки"""
        return False if self.condition in ('T', 'X') else True

    @property
    def neighbours(self):
        """Геттер количества кораблей по соседству"""
        return self.__neighbours

    @condition.setter
    def condition(self, value):
        """Сеттер состояния клетки"""
        self.__condition = value

    @neighbours.setter
    def neighbours(self, value):
        """Сеттер количества кораблей по соседству"""
        self.__neighbours = value

    @property
    def owning_ship(self):
        """Геттер корабля-"хозяина" клеткис"""
        return self.__owning_ship

    @owning_ship.setter
    def owning_ship(self, value):
        """Сеттер корабля-"хозяина" клеткис"""
        self.__owning_ship = value


class Ship:
    """Класс корабля"""

    def __init__(self, deck_list):  # Конструктор класса
        self.decks = []  # Объявление списка палуб корабля (объекты Point)
        for deck in deck_list:  # Заполнение списка палуб корабля (объекты Point)
            deck.condition = '■'  # Исходно все палубы "целые"
            self.decks.append(deck)

    @property
    def size(self):
        """Геттер размера корабля"""
        return len(self.decks)

    def get_deck(self, num):
        """Геттер палубы"""
        return self.decks[num]

    def set_deck(self, num, value):
        """Сеттер состояния палубы"""
        self.decks[num].condition = value

    def wreck_check(self):
        """Метод проверки, не убит ли корабль"""
        for deck in self.decks:
            if deck.condition != 'X':
                return False
        return True

    def wound_check(self):
        """Метод проверки, не ранен ли корабль"""
        result = False  # Результат по умолчанию "ложь"
        wounded = 0  # Счетчик раненых клеток
        alive = 0  # Счетчик целых клеток
        for deck in self.decks:  # Среди палуб корабля ищутся целые и раненные
            if deck.condition == 'X':
                wounded += 1
            else:
                alive += 1
            if wounded and alive:  # Если найдены и целые и раненные, результат подтвержден: корабль ранен
                result = True
                break  # Прерывание цикла
        return result


class Board:
    """Класс игрового поля"""

    def __init__(self, owner, visible, side_size=BOARD_SIZE, fleet_compos=FLEET_COMPOSITION):
        """Конструктор класса"""
        self.fleet = []  # Флот кораблей (объекты Ship)
        self.owner = owner  # Имя хозяина поля
        self.side_size = side_size  # Размер поля
        self.fleet_compos = fleet_compos  # Состав флота
        self.col_headers = ([' ' * len(str(self.side_size))] +
                            (list(string.ascii_uppercase)[:self.side_size]))  # Заголовки столбцов
        self.visible = visible  # Видимость поля
        self.points = [[Point(col, row) for row in range(self.side_size)]
                       for col in range(self.side_size)]  # Матрица всех клеток доски (объекты Point)

    def range_check(self, *coords):
        """Метод проверки нахождения координат в рамках поля"""
        for coord in coords:
            if coord not in range(self.side_size):
                return False
        return True

    def place_ship(self, x0, y0, xk, yk):
        """Метод размещения корабля"""
        ship_decks = []  # Объявление списка палуб корабля
        if self.range_check(x0, y0, xk, yk):  # Проверка нахождения добавляемой палубы в рамках поля
            for x in range(min(x0, xk), max(x0, xk) + 1):
                for y in range(min(y0, yk), max(y0, yk) + 1):
                    if self.points[x][y].neighbours == 0:  # Проверка допустимости расположения палубы в клетке
                        ship_decks.append(self.points[x][y])  # Добавление палубы к списку палуб корабля
                    else:
                        raise ValueError('Здесь нельзя разместить корабль!')
        else:
            raise ValueError('Корабль выходит за границы игрового поля!')
        ship = Ship(ship_decks)  # Создания корабля с заданным расположением
        self.fleet.append(ship)  # Добавление корабля к списку кораблей игрового поля
        for i in range(ship.size):  # Задание "хозяина" палубам корабля
            ship.get_deck(i).owning_ship = ship
        for x in range(min(x0, xk) - 1, max(x0, xk) + 2):
            for y in range(min(y0, yk) - 1, max(y0, yk) + 2):
                if self.range_check(x, y):  # Проверка нахождения клетки в поле во избежание ошибок индекса
                    self.points[x][y].neighbours += 1  # Увеличение количества "соседних" с клеткой кораблей

    def unplace_ship(self):
        """Метод удаления корабля"""
        ship = self.fleet[-1]  # Работает с последним добавленным кораблем
        for i in range(ship.size):
            ship.get_deck(i).condition = 'O'  # Возврат клеток в исходное состояние
            ship.get_deck(i).owning_ship = None
        for x in range(ship.get_deck(0).x - 1, ship.get_deck(-1).x + 2):
            for y in range(ship.get_deck(0).y - 1, ship.get_deck(-1).y + 2):
                if self.range_check(x, y):  # Проверка нахождения клетки в поле во избежание ошибок индекса
                    self.points[x][y].neighbours -= 1  # Уменьшение количества "соседних" с клеткой кораблей
        self.fleet.pop()  # Удаление корабля из списка кораблей поля

    def input_to_coords(self, user_input, n):
        """Метод преобразования введенных пользователем координат n точек в координаты матрицы клеток поля"""
        coord_list = user_input.split()  # Преобразование ввода в список
        result = []  # Объявление списка координат
        if len(coord_list) != 2 * n:  # Проверка правильности количества введенных координат
            raise ValueError('Неверный ввод!')
        for i in range(n):  # Проверка правильности ввода
            try:
                y = int(coord_list[2 * i + 1]) - 1  # Проверка того, что вторая координата является целым числом
            except ValueError:
                raise ValueError('Неверный ввод!')
            if not(coord_list[2 * i] in self.col_headers[1:] and  # Проверка того, что координаты в нужных пределах
                   self.range_check(y)):
                raise ValueError('Неверный ввод!')
            else:  # Добавление точки к кортежу координат
                result += [self.col_headers.index(coord_list[2 * i]) - 1, y]
        return tuple(result)  # Возврат кортежа координат

    def user_fill(self):
        """Метод заполнения доски пользователем"""
        ships_remaining = {}  # Словарь длин кораблей, оставшихся к размещению
        remaining = 0  # Переменная, хранящей общее число оставшихся кораблей
        for length in self.fleet_compos.keys():
            ships_remaining[length] = self.fleet_compos[length]
            remaining += ships_remaining[length]
        print(f'Начинаем расстановку кораблей игрока {self.owner}.')  # Вывод справочной информации
        print('Для размещения корабля введите координаты его начальной и конечной точек (например: A 1 B 1).')
        print('Для отмены размещения предыдущего корабля введите "Undo".')
        print_separator(100)  # Вывод разделителя
        self.print_board()  # Распечатка игрового поля (исходно пустого)
        while remaining > 0:
            print('Осталось расположить:')  # Вывод информации об оставшихся кораблях
            for length in ships_remaining.keys():
                print(f'{length}-палубных: {ships_remaining[length]}')
            user_input = input('Координаты нового корабля: ').upper()  # Считывание ввода (нечуствительно к регистру)
            try:  # Отлов всех предусмотренных исключений
                if user_input == 'UNDO':  # В случае введения команды отмены
                    if len(self.fleet) == 0:
                        raise ValueError('Отменять нечего: вы не расположили ни одного корабля.')
                    else:  # Возврат на шаг назад и удаление последнего корабля
                        ships_remaining[self.fleet[-1].size] += 1
                        remaining += 1
                        self.unplace_ship()
                        print('Размещение корабля отменено.')
                else:  # Если нет команды отмены, ввод рассматривается как координаты
                    x0, y0, xk, yk = self.input_to_coords(user_input, 2)
                    width = min(abs(x0 - xk), abs(y0 - yk)) + 1  # Ширина введенного корабля
                    length = max(abs(x0 - xk), abs(y0 - yk)) + 1  # Длина введенного корабля
                    if width > 1:  # Ширина должна быть = 1
                        raise ValueError('Все палубы корабля должны располагаться на одной линии!')
                    elif length not in ships_remaining.keys():  # Длина должна быть предусмотрена составом флота
                        raise ValueError(f'{length}-палубные корабли не предусмотрены!')
                    elif ships_remaining[length] == 0:  # Проверка, нужны ли еще корабли такой длины
                        raise ValueError(f'Вы уже разместили все корабли длины {length}!')
                    else:  # Размещение корабля после всех проверок
                        self.place_ship(x0, y0, xk, yk)
                        ships_remaining[length] -= 1
                        remaining -= 1
                        print(f'{length}-палубный корабль успешно размещен.')
            except ValueError as err:  # В случае вызова исключения вывод ошибки
                print(f'Ошибка: {err}')
            print_separator(100)  # Вывод разделителя
            self.print_board()  # Распечатка текущего игрового поля
        print(f'Расстановка кораблей игрока {self.owner} закончена.')

    def generate_placements(self, length, width=1):
        """Метод формирования списка возможных расположений корабля длины length и ширины width (по умолчанию 1)"""
        result = set()  # Объявление списка, в который записываются все годные варианты расположения
        for x0 in range(self.side_size):  # Для каждой клетки поля проверяются варианты размещения вниз и вправо
            for y0 in range(self.side_size):
                for delta_x in range(length):  # Проверка возможности размещения вправо от x0, y0
                    placable = True
                    for delta_y in range(width):
                        x = x0 + delta_x  # Координаты текущей проверяемой палубы
                        y = y0 + delta_y
                        if not self.range_check(x, y):  # Проверка, в поле ли палуба
                            placable = False
                            break
                        elif self.points[x][y].neighbours > 0:  # Нет ли по соседству с палубой другого корабля
                            placable = False
                            break
                    if not placable:  # Если какая-либо проверка не прошла, разместить вправо от x0, y0 нельзя
                        break
                else:  # Если все проверки прошли
                    result.add((x0, y0, x0 + length - 1, y0 + width - 1))  # Вариант добавляется к результату
                for delta_y in range(length):  # Проверка возможности размещения вниз от x0, y0
                    placable = True
                    for delta_x in range(width):
                        x = x0 + delta_x  # Координаты текущей проверяемой палубы
                        y = y0 + delta_y
                        if not self.range_check(x, y):  # В поле ли клетка
                            placable = False
                            break
                        elif self.points[x][y].neighbours > 0:  # Нет ли по соседству с палубой другого корабля
                            placable = False
                            break
                    if not placable:
                        break
                else:  # Если все проверки прошли
                    result.add((x0, y0, x0 + width - 1, y0 + length - 1))  # Вариант добавляется к результату
        return result  # Возврат множества всех прошедших проверку вариантов

    def generate_shootable(self):
        """Метод генерации множества всех клеток, по которым можно стрелять.
           Если есть недобитый корабль, стрелять по нему"""
        result = set()  # Объявление множества клеток координат, по которым можно стрелять
        wounded_decks = []  # Объявление массива подбитых клеток раненого корабля
        for ship in self.fleet:  # Поиск раненого корабля
            if ship.wound_check():
                for deck_index in range(ship.size):  # Поиск и обавление палуб раненого корабля к массиву
                    deck = ship.get_deck(deck_index)
                    if deck.condition == 'X':
                        wounded_decks.append(deck)
                break  # Если раненый корабль нашелся, искать дальше нет смысла
        if wounded_decks:  # Если найдены палубы раненого корабля
            min_point, max_point = wounded_decks[0], wounded_decks[-1]  # Первая и последняя раненные палубы
            if min_point.x == max_point.x:  # Если раненные палубы стоят по вертикали
                for coords in ((min_point.x, min_point.y - 1), (max_point.x, max_point.y + 1)):
                    if self.range_check(*coords) and self.points[coords[0]][coords[1]].shootable:
                        result.add(coords)  # Проверка и добавление к резульату соседних с ними по вертикали клеток
            if min_point.y == max_point.y:  # Если раненные палубы стоят по горизонтали
                for coords in ((min_point.x - 1, min_point.y), (max_point.x + 1, max_point.y)):
                    if self.range_check(*coords) and self.points[coords[0]][coords[1]].shootable:
                        result.add(coords)  # Проверка и добавление к резульату соседних с ними по горизонтали клеток
        else:  # Если раненных кораблей нет
            for x in range(self.side_size):
                for y in range(self.side_size):
                    if self.points[x][y].shootable:
                        result.add((x, y))  # К результату добавляются все клетки, по которым можно стрелять
        return result  # Возвращение результата

    def auto_fill(self):
        """Метод автоматического заполнения игрового поля"""
        length_list = []  # Список длин всех кораблей, которые надо разместить
        possible_placements = []  # Список, содержащих множества возможных расположений для каждого шага расстановки
        total_steps = 0  # Объявление переменной, хранящей количество необходимых шагов
        for length in self.fleet_compos.keys():  # Заполнение переменных
            length_list += [length] * self.fleet_compos[length]
            total_steps += self.fleet_compos[length]
        step = 0  # Объявление переменной, хранящей номер текущего шага
        steps = 0  # Объявление счетчика потребовавшихся шагов
        while step < total_steps:  # Условие успешного окончания расстановки
            if len(possible_placements) <= step:  # Если для текущего шага нет множества возможных расположений, создать
                possible_placements.append(self.generate_placements(length_list[step]))
            if not possible_placements[step]:  # Если для текущего шага множества возможных расположений пустое
                if step == 0:  # Если шаг первый, расстановка в принципе невозможна
                    raise ValueError('Расстановка кораблей с заданными настройками невозможна')
                else:  # Если шаг не первый, алгоритм зашел в тупик и надо вернуться на шаг назад
                    possible_placements.pop()  # Множество (пустое) возможных расположений для текущего шага удаляется
                    step -= 1  # Возврат на шаг назад
                    ship = self.fleet[-1]  # Последний размещенный корабль не подходит
                    # Его координаты удаляются из множества возможных расположений для предыдущего шага
                    possible_placements[step].discard((ship.get_deck(0).x, ship.get_deck(0).y,
                                                       ship.get_deck(-1).x, ship.get_deck(-1).y))
                    self.unplace_ship()  # Размещение корабля отменяется
            else:  # Если множество возможных расположений не пустое
                self.place_ship(*choice(list(possible_placements[step])))  # Размещается случайный корабль из возможных
                step += 1  # Переход на следующий шаг
                steps += 1  # Увеличение счетчика затраченных шагов
            if self.visible:  # Для тестера на каждом шаге выводится номер шага и поле с разделителем
                print(f'Шаг {steps}:')
                self.print_board()
                print_separator(100)
        print(f'Автоматическая расстановка кораблей игрока {self.owner} прошла успешно.')  # Окончание алгоритма

    def fill(self):
        """Метод выбора и реализации способа заполнения в зависимости от хозяина доски"""
        if self.owner.lower() == 'computer':
            self.auto_fill()
        else:
            self.user_fill()

    def print_board(self):
        """Метод вывода игрового поля"""
        print('|'.join(self.col_headers) + '|')  # Распечатка строки заголовков столбцов
        for row in range(self.side_size):
            spaces = ' ' * (len(str(self.side_size)) - len(str(row + 1)))  # Для выравнивания если размер больше 9
            print(f'{row + 1}{spaces}|', end='')  # Распечатка номера строки
            for col in range(self.side_size):  # Распечатка клеток строки (в зависимости от их видимости для игрока)
                if self.points[col][row].condition == '■':
                    print((self.points[col][row].condition if self.visible else 'O') + '|', end='')
                else:
                    print(self.points[col][row].condition + '|', end='')
            print()

    def shoot(self, x0, y0):
        """Метод стрельбы по клетке с заданными координатами"""
        point = self.points[x0][y0]  # Клетка, по которой будет проводиться стрельба
        if not point.shootable:  # Проверка, можно ли стрелять по клетке
            raise ValueError('По этой клетке больше нельзя стрелять!')  # Если нет, вызвать ошибку
        elif point.condition == '■':  # Если клетка является целой палубой (убил/ранил)
            point.condition = 'X'  # Смена состояния клетки на подбитую палубу
            ship = point.owning_ship  # Корабль, которому принадлежит палуба
            if ship.wreck_check():  # Проверка, убит ли корабль
                for deck_index in range(ship.size):  # Соседние клетки с палубами корабля получают состояние "мимо"
                    for x in range(ship.get_deck(deck_index).x - 1, ship.get_deck(deck_index).x + 2):
                        for y in range(ship.get_deck(deck_index).y - 1, ship.get_deck(deck_index).y + 2):
                            if self.range_check(x, y) and not self.points[x][y].owning_ship:
                                self.points[x][y].condition = 'T'
                print('Убил!')  # Вывод результата стрельбы
            else:  # Если корабль не убит
                print('Ранил!')  # Вывод результата стрельбы
            return True
        else:  # Если клетка пуста (промах)
            point.condition = 'T'
            print('Мимо!')  # Вывод результата стрельбы
            return False

    def get_owner(self):
        return self.owner

    def get_row(self, n):
        """Геттер заголовка столбца по координате"""
        return self.col_headers[n + 1]

    @property
    def defeat(self):
        """Геттер поражения данной доски"""
        for ship in self.fleet:  # Все корабли должны быть убиты, иначе доска еще не проиграла
            if not ship.wreck_check():
                return False
        return True


def switch(a, b):
    """Генератор бесконечного чередования двух значений"""
    while True:
        yield a
        yield b


def print_interface(board1, board2):
    """Функция распечатки интерфейса, состоящего из двух полей, их заголовков и разделителя"""
    for board in (board1, board2):
        print()
        print(f'Поле игрока {board.get_owner()}')
        board.print_board()
    print_separator(100)


player_1_name = input('Введите Ваше имя для начала игры: ')  # Ввод имени игрока
board_1 = Board(player_1_name, True)  # Инициализация игрового поля игрока

if player_1_name.lower() == 'tester':  # Если игрок вошел под именем tester, игра ведется в открытую
    player_2_name = input('Вы вошли в режим тестирования игры в открытую. Введите имя второго игрока или "Computer": ')
    board_2 = Board(player_2_name, True)  # Инициализация открытого игрового поля, управляемого игроком или компьютером
else:  # Второму игроку по умолчанию присваивается имя Computer
    player_2_name = 'Computer'
    board_2 = Board(player_2_name, False)  # Инициализация игрового поля компьютера

board_1.fill()  # Заполнение и вывод игровых полей
board_2.fill()
print_separator(100)
print_interface(board_1, board_2)

print('Начинаем игру.')
print('Чтобы сделать выстрел, введите координаты клетки (например: A 1)')
board_switch = switch(board_2, board_1)  # Переключатель текущей обстреливаемой доски
shooter_switch = switch(board_1.get_owner(), board_2.get_owner())  # Переключатель текущего игрока, выполняющего выстрел
game_end = False  # Условие окончания игры по умолчанию не выполняется
while True:  # Основной цикл игры
    current_board = next(board_switch)  # Текущая обстреливаемая доска
    shooter = next(shooter_switch)  # Переключатель текущий игрок, выполняющий выстрел
    go_on = True  # Условие продолжения хода по умолчанию выполняется
    while go_on:  # Цикл стрельбы
        print(f'Ход игрока {shooter}.')
        try:
            if shooter.lower() == 'computer':  # Компьютер стреляет автоматически
                x_shoot, y_shoot = choice(list(current_board.generate_shootable()))  # Случайный выбор координат
                print(f'Координаты клетки для обстрела: {current_board.get_row(x_shoot)} {str(y_shoot + 1)}', end='')
                input()  # От пользователя требуется нажать Enter после прочтения хода компьютера
                go_on = current_board.shoot(x_shoot, y_shoot)  # Выполнение стрельбы и проверка попадания
            else:  # Пользователь стреляет по вводимым координатам
                coordinates = input('Координаты клетки для обстрела: ').upper()  # Считывание ввода
                x_shoot, y_shoot = current_board.input_to_coords(coordinates, 1)  # Преобразование ввода в координаты
                go_on = current_board.shoot(x_shoot, y_shoot)  # Выполнение стрельбы и проверка попадания
        except ValueError as e:  # В случае неправильного ввода выводится ошибка, ход повторяется
            print(f'Ошибка: {e}')
        else:
            print_interface(board_1, board_2)  # Если ошибки нет, выводится обновленный интерфейс
        if current_board.defeat:  # Если после выстрела все корабли убиты, стрельба завершается и игра оканчивается
            go_on = False
            game_end = True
    if game_end:
        print(f'Игра окончена. Победил игрок {shooter}')
        break
