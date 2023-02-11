import numpy as np
import turtle
import uuid
from typing import Any

SPEED = {'scout': 45, 'warrior': 60, 'healer': 60, 'king': 0}
MAX_SPEED = {'scout': 90, 'warrior': 150, 'healer': 210, 'king': 0}
MAX_HEALTH = {'scout': 70, 'warrior': 100, 'healer': 100, 'king': 100}
ATTACK = {'scout': 20, 'warrior': 30, 'healer': 10, 'king': 0}
VIEW_RADIUS = {'scout': 150, 'warrior': 100, 'healer': 100, 'king': 0}


class Knight:

    def __init__(self, x: int, y: int, name: str, heading: float, team: str,
                 castle: dict, fountain: dict, number: int, AI: Any):
        self.avatar = turtle.Turtle()
        self.avatar.speed(0)
        self.avatar.penup()

        self.avatar_circle = turtle.Turtle()
        self.avatar_circle.speed(0)
        self.avatar_circle.penup()
        self.avatar_circle.hideturtle()
        self.avatar_circle.setheading(270)

        self.avatar_name = turtle.Turtle()
        self.avatar_name.speed(0)
        self.avatar_name.penup()
        self.avatar_name.hideturtle()

        self.avatar.setx(x)
        self.avatar.sety(y)
        self.heading = heading
        self.team = team
        self.name = name
        self.cooldown = 0
        self.avatar.color(self.team)
        self.avatar_circle.color(self.team)
        self.avatar_name.color(self.team)

        self.castle = castle
        self.fountain = fountain
        self.number = number

        self.ai = AI(team=team)
        self.kind = self.ai.kind

        self.speed = SPEED[self.kind]
        self.max_speed = MAX_SPEED[self.kind]
        self.max_health = MAX_HEALTH[self.kind]
        self.attack = ATTACK[self.kind]
        self.view_radius = VIEW_RADIUS[self.kind]
        self.health = self.max_health
        self.id = uuid.uuid4().hex

    def __repr__(self) -> str:
        return (f'{self.name}: H:{self.health}/{self.max_health} '
                f'A:{self.attack} S:{self.speed} at {self.x}, {self.y}')

    def __str__(self) -> str:
        return repr(self)

    @property
    def x(self) -> int:
        return int(self.avatar.xcor())

    @property
    def y(self) -> int:
        return int(self.avatar.ycor())

    @property
    def position(self) -> np.ndarray:
        return np.array(self.avatar.position()).astype(int)

    @property
    def heading(self) -> float:
        return self.avatar.heading()

    @heading.setter
    def heading(self, angle: float):
        return self.avatar.setheading(angle)

    @property
    def vector(self) -> np.ndarray:
        h = self.heading * np.pi / 180.0
        return np.array([np.cos(h), np.sin(h)])

    def ray_trace(self, dt: float) -> np.ndarray:
        vt = self.speed * dt
        ray = self.vector.reshape((2, 1)) * np.linspace(1, vt, int(vt) + 1)
        return (np.array(self.avatar.position()).reshape((2, 1)) + ray).astype(int)

    def get_distance(self, pos: tuple) -> float:
        return np.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)

    def advance_dt(self, t: float, dt: float, info: dict):
        self.cooldown = max(self.cooldown - dt, 0)
        if self.avatar.distance(self.fountain['x'],
                                self.fountain['y']) <= self.fountain['size']:
            self.heal(15. * dt)
        if self.kind == 'healer':
            for friend in info['friends']:
                if (self.get_distance(friend.position) <
                        self.view_radius) and (friend.kind != 'king'):
                    friend.heal(5. * dt)

    def execute_ai(self, t: float, dt: float, info: dict, safe: bool = False):
        if safe:
            try:
                self.ai.exec(t, dt, info)
            except:
                pass
        else:
            self.ai.exec(t, dt, info)
        if not safe:
            nprops = 0
            if self.ai.heading is not None:
                nprops += 1
            if self.ai.goto is not None:
                nprops += 1
            if self.ai.left is not None:
                nprops += 1
            if self.ai.right is not None:
                nprops += 1
            if nprops > 1:
                print('Warning, more than one AI property is set, '
                      'results may be unpredictable!')
        # try:
        if self.ai.heading is not None:
            self.heading = self.ai.heading
        if self.ai.goto is not None:
            self.goto(*self.ai.goto)
        if self.ai.left is not None:
            self.left(self.ai.left)
        if self.ai.right is not None:
            self.right(self.ai.right)
        # except:
        #     print('Error in ', self.ai.creator, self.name)
        #     pass

    def heal(self, value: float):
        self.health = min(self.max_health, self.health + value)

    def draw_circle(self):
        self.avatar_circle.clear()
        if self.cooldown > 0:
            self.avatar_circle.color('cyan')
        self.avatar_circle.goto(self.x - self.view_radius, self.y)
        self.avatar_circle.pendown()
        self.avatar_circle.circle(self.view_radius, steps=20)
        self.avatar_circle.penup()
        self.avatar_circle.color(self.team)

    def draw_name(self):
        self.avatar_name.clear()
        self.avatar_name.goto(self.x, self.y)
        self.avatar_name.pendown()
        self.avatar_name.write(self.name,
                               move=False,
                               align="center",
                               font=('Arial', 12, 'normal'))
        self.avatar_name.penup()

    def move(self, dt: float):
        self.avatar.forward(self.speed * dt)
        self.draw_circle()
        self.draw_name()

    def goto(self, x: float, y: float):
        angle = self.avatar.towards(x, y)
        self.heading = angle

    def towards(self, x: float, y: float) -> float:
        return self.avatar.towards(x, y)

    def right(self, angle: float):
        self.avatar.right(angle)

    def left(self, angle: float):
        self.avatar.left(angle)
