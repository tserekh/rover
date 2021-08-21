import sys
import logging
from collections import defaultdict
from typing import List
from functools import reduce
import time
mode = 'dev'

start_time = time.time()
if mode=='dev':
    logging.basicConfig(filename='logfile.log', level=logging.DEBUG)
    # logging.basicConfig(filename='logfile.log', level=logging.CRITICAL)
else:
    logging.basicConfig(filename='logfile.log', level=logging.CRITICAL)


class Point:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def show(self):
        sys.stdout.write(f'{self.row} {self.col}\n')
        sys.stdout.flush()


class Rover(Point):
    def __init__(self, row: int, col: int, N: int):
        self.row = row
        self.col = col
        self.w_cargo = False
        self.empty = True
        self.N = N
        self.take_row_history =[]
        self.take_col_history = []
        self.put_row_history = []
        self.put_col_history = []

    def check(self):
        assert self.row >= 1, self.row
        assert self.row <= self.N, self.row
        assert self.col >= 1, self.col
        assert self.col <= self.N, self.col

    def move(self, action_letter: str):
        if action_letter == "U":
            self.row -= 1
        elif action_letter == "L":
            self.col -= 1
        elif action_letter == "D":
            self.row += 1
        elif action_letter == "R":
            self.col += 1
        elif action_letter == "S":
            pass
        self.check()

    def take_put(self, take_put_letter: str):
        if take_put_letter == "T":
            self.empty = False
            self.take_row_history.append(self.row)
            self.take_col_history.append(self.col)
            logging.info(f'take at {self.row} {self.col} empty {self.empty}')
        elif take_put_letter == "P":
            self.empty = True
            self.put_row_history.append(self.row)
            self.put_col_history.append(self.col)
            logging.info(f'put at {self.row} {self.col} empty {self.empty}')

    def action(self, action_letter: str):
        if action_letter in "ULDRS":
            self.move(action_letter)
        elif action_letter in "TP":
            self.take_put(action_letter)

    def actions(self, route: str):
        for letter_ in route:
            self.action(letter_)


class Order:
    def __init__(self, start_point: Point, finish_point: Point, created_time: int):
        self.start_point = start_point
        self.finish_point = finish_point
        self.created_time = created_time
        self.done = False

    def referesh_possible_income(self, rover_point: Point, max_tips, current_time):
        distance = get_distance(rover_point, self.start_point) + get_distance(self.start_point, self.finish_point)
        self.possible_income = max_tips + self.created_time - current_time - distance


def get_center(city):
    N = len(city)
    point = Point(N//2, N//2)
    if city[point.row - 1][point.col -1] == '.':
        logging.info(f'city center {point.row} {point.col}')
        return point
    for j, row in enumerate(city):
        for k, letter in enumerate(row):
            if letter == '.':
                point = Point(j + 1, k + 1)
                logging.info(f'city center {point.row} {point.col}')
                return Point(j+1, k+1)


def make_graph(city: List[str]):
    unique_values = reduce(lambda x, y: x | y, list(map(set, city)))
    if '#' not in unique_values:
        return None
    graph = defaultdict(set)
    N = len(city)
    for i in range(N):
        for j in range(N):
            if ((i+1)<N) & (city[i][j] == '.') and (city[i+1][j] == '.'):
                graph[f"{i+1}_{j+1}"].add(f"{i+2}_{j+1}")
                graph[f"{i+2}_{j+1}"].add(f"{i+1}_{j+1}")
            if ((j+1)<N) and (city[i][j] == '.') and (city[i][j+1] == '.'):
                graph[f"{i+1}_{j+1}"].add(f"{i+1}_{j+2}")
                graph[f"{i+1}_{j+2}"].add(f"{i+1}_{j+1}")
    return graph


def get_simple_route(A: Point, B: Point) -> str:
    """
    From A to B
    """
    row_diff = B.row - A.row
    col_diff = B.col - A.col
    logging.info(f'get route from {A.row} {A.col} to {B.row} {B.col}')

    route = ''
    if row_diff > 0:
        route = route + row_diff * 'D'
    elif row_diff < 0:
        route = route + (-row_diff) * 'U'
    if col_diff > 0:
        route = route + col_diff * 'R'
    elif col_diff < 0:
        route = route + (-col_diff) * 'L'
    logging.info(f'route {route}')
    return route


def shortest_path(graph, source: str, target: str):
    path_dict = defaultdict(lambda: [source])
    path_dict[source] = [source]
    done = False
    for i in range(N*N):
        keys = list(path_dict.keys())
        if target in keys:
            keys = [target]
        for k in keys:
            for node_ in graph[k]:
                if node_ not in path_dict.keys():
                    path_dict[node_] = path_dict[k] + [node_]
                if node_ == target:
                    done = True
                    break
        if done:
            break
    path = path_dict[target]
    return path


def get_route(graph, begin_point: Point, end_point: Point) -> str:
    if city_graph is None:
        return get_simple_route(begin_point, end_point)
    path = shortest_path(graph, f'{begin_point.row}_{begin_point.col}', f'{end_point.row}_{end_point.col}')
    route = ''
    for i in range(len(path) - 1):
        point1 = path[i].split('_')
        point2 = path[i + 1].split('_')

        point1[0] = int(point1[0])
        point1[1] = int(point1[1])
        point2[0] = int(point2[0])
        point2[1] = int(point2[1])

        point1 = Point(*point1)
        point2 = Point(*point2)

        route += get_simple_route(point1, point2)

    return route


def get_distance(A_point: Point, B_point: Point) -> int:
    return abs(A_point.row - B_point.row) + abs(A_point.col - B_point.col)


if __name__=='__main__':
    filename = '04.txt'
    output = open('output.txt', 'w')
    if mode == 'prod':
        filename = 'input.txt'
    if mode == 'dev':
        reader = open(filename, 'r')
    elif mode == 'prod':
        reader = sys.stdin

    N, max_tips, cost = reader.readline()[:-1].split(' ')
    N = int(N)
    max_tips = int(max_tips)
    cost = int(cost)
    city = []
    for i in range(N):
        city.append(reader.readline()[:-1])
    city_graph = make_graph(city)
    logging.info(str(city_graph)[:100])
    T, D = reader.readline()[:-1].split(' ')
    T = int(T)
    D = int(D)

    n_rovers = 1
    sec_in_min = 60
    city_center = get_center(city)
    logging.info(f"city center {city_center.row}  {city_center.col}")
    rover = Rover(city_center.row, city_center.col, N)
    sys.stdout.write(f'{n_rovers}\n')
    sys.stdout.flush()

    rover.show()

    orders_list = []
    for t in range(T):
        if (time.time()-start_time) > 19.0:
            sys.stdout.write(sec_in_min*'S'+'\n')
            if mode == 'dev':
                sys.stdout.write('!!!!!!!!! force end !!!!!!!!!!')
                break
            else:
                continue
        logging.info('')
        logging.info(f'minute {t}')
        logging.info(f'rover empty {rover.empty}')
        route = ''
        n_new_orders = int(reader.readline()[:-1])
        for _ in range(n_new_orders):
            s_row, s_col, f_row, f_col = tuple(map(int, reader.readline()[:-1].split(' ')))
            start_point = Point(s_row, s_col)
            finish_point = Point(f_row, f_col)
            order = Order(start_point, finish_point, t * sec_in_min)
            order.possible_income = 0
            if (city_graph is None) or (get_distance(start_point, finish_point) < 40):
                orders_list.append(order)

        if rover.empty:
            orders_list = list(filter(lambda x: x.done == False, orders_list))
            for i in range(len(orders_list)):
                orders_list[i].referesh_possible_income(rover, max_tips, t*sec_in_min)
            orders_list = list(filter(lambda x: x.possible_income >= 0, orders_list))
            orders_list = sorted(orders_list, key=lambda x: x.possible_income, reverse=True)
            if len(orders_list) == 0:
                sys.stdout.write('S'*sec_in_min+'\n')
                sys.stdout.flush()
                continue
            else:
                current_order = orders_list[0]
        logging.info(f'current_order {current_order.start_point.row} {current_order.start_point.col} {current_order.finish_point.row} {current_order.finish_point.col}')
        if rover.empty:
            route += get_route(city_graph, rover, current_order.start_point)
            route += "T"
            route += get_route(city_graph, current_order.start_point, current_order.finish_point)
            route += "P"
        else:
            route += get_route(city_graph, rover, current_order.finish_point)
            route += "P"

        if len(route) > 60:
            route = route[:60]
        route = route + "S" * (sec_in_min - len(route))

        for letter in route:
            rover.action(letter)

        if mode=='dev':
            sys.stdout.write(f'{route}\n'.replace('T', ' T ').replace('P', ' P '))
        elif mode=='prod':
            sys.stdout.write(f'{route}\n')
        sys.stdout.flush()
        if "P" in route:
            orders_list[0].done = True
            assert current_order.finish_point.row == rover.row, f"row {current_order.finish_point.row}=={rover.row} {rover.take_row_history} {rover.take_col_history} {rover.put_col_history} {rover.put_row_history}"
            assert current_order.finish_point.col == rover.col, f"col {current_order.finish_point.col}=={rover.col} {rover.take_row_history} {rover.take_col_history} {rover.put_col_history} {rover.put_row_history}"
    output.close()
