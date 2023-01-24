import numpy as np


class BaseAI:

    def __init__(self, kind: str, creator: str, team: str = None):
        self.team = team
        self.opposing_team = 'red' if self.team == 'blue' else 'blue'
        self.kind = kind.lower()
        self.heading = None
        self.goto = None
        self.message = None
        self.creator = creator
        self.stop = False
        self.left = None
        self.right = None

    def exec(self, t: float, dt: float, info: dict):
        self.heading = None
        self.goto = None
        self.left = None
        self.right = None
        self._params = info['me']
        self.run(t=t, dt=dt, info=info)

    def get_distance(self, x: float, y: float = None) -> float:
        if y is None:
            y = x[1]
            x = x[0]
        return np.sqrt((self._params['x'] - x)**2 + (self._params['y'] - y)**2)

    def towards(self, x: float, y: float = None) -> float:
        if y is None:
            y = x[1]
            x = x[0]
        return ((np.arctan2(y - self._params['y'], x - self._params['x']) *
                 180 / np.pi) + 360) % 360

    def heading_from_vector(vec: np.ndarray) -> float:
        return ((np.arctan2(vec[1], vec[0]) * 180 / np.pi) + 360) % 360

    def vector_from_heading(heading: float) -> np.ndarray:
        h = heading * np.pi / 180.0
        return np.array([np.cos(h), np.sin(h)])
