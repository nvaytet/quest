import numpy as np


class Map:

    def __init__(self, nx: int, ny: int, ng: int):
        self.nx = nx
        self.ny = ny
        self.ng = ng
        self.array = np.zeros((nx, ny), dtype=int)
        self._make_obstacles()
        self._make_castles()
        self._make_fountains()
        self._make_gems()

    def _make_obstacles(self, n: int = 100):
        free_zone = 200
        posx = np.random.random(n) * (self.nx - (2 * free_zone)) + free_zone
        posy = np.random.random(n) * self.ny
        dx = 40

        for k in range(n):
            ic = int(posx[k])
            jc = int(posy[k])
            for i in range(max(int(ic - 0.5 * dx), 0), min(int(ic + 0.5 * dx),
                                                           self.nx)):
                for j in range(max(int(jc - 0.5 * dx), 0),
                               min(int(jc + 0.5 * dx), self.ny)):
                    self.array[i, j] = 1
        self._obstacles = {'x': posx, 'y': posy, 'dx': dx}

    def _make_gems(self, n: int = 100):
        posx = np.zeros(n, dtype=int)
        posy = np.zeros(n, dtype=int)
        for i in range(n):
            not_good = True
            while not_good:
                x = int(np.random.random() * (self.nx - 1))
                y = int(np.random.random() * (self.ny - 1))
                if self.array[x, y] == 0:
                    self.array[x, y] = 2
                    posx[i] = x
                    posy[i] = y
                    not_good = False
        self._gems = {'x': posx, 'y': posy}

    def _make_castles(self):
        dx = 80
        thickness = 10
        dir_choice = np.random.choice([0, 1, 2, 3])
        directions = [[0, 2], [1, 1], [2, 0], [3, 3]]
        d = directions[dir_choice]

        x = []
        y = []

        for i in range(2):
            posx = np.random.randint(2, 4) * self.ng + 0.5 * self.ng
            if i == 1:
                posx = self.nx - posx
            posy = np.random.randint(2,
                                     self.ny // self.ng - 2) * self.ng + 0.5 * self.ng

            self.array[int(posx - 0.5 * dx):int(posx + 0.5 * dx),
                       int(posy - 0.5 * dx):int(posy + 0.5 * dx)] = 1
            self.array[int(posx - 0.5 * dx) +
                       (thickness * int(d[i] != 2)):int(posx + 0.5 * dx) -
                       (thickness * int(d[i] != 0)),
                       int(posy - 0.5 * dx) +
                       (thickness * int(d[i] != 3)):int(posy + 0.5 * dx) -
                       (thickness * int(d[i] != 1))] = 0
            x.append(posx)
            y.append(posy)

        self._castles = {
            'dx': dx,
            'thickness': thickness,
            'red': {
                'x': x[0],
                'y': y[0],
                'direction': d[0],
            },
            'blue': {
                'x': x[1],
                'y': y[1],
                'direction': d[1]
            }
        }

        self._flags = {'red': [x[0], y[0]], 'blue': [x[1], y[1]]}

    def _make_fountains(self):
        dist = self.ny // 3
        size = 100
        self._fountains = {}
        for team in ('red', 'blue'):
            posx = self._castles[team]['x']
            posy = self._castles[team]['y'] - dist if self._castles[team]['y'] > (
                self.ny // 2) else self._castles[team]['y'] + dist
            self._fountains[team] = {'x': posx, 'y': posy, 'size': size}
