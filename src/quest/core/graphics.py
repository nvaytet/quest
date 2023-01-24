import turtle
from typing import Any


def rectangle(pen: Any,
              x: float,
              y: float,
              dx: float,
              dy: float,
              color: str,
              fill=False):
    pen.penup()
    pen.setheading(0)
    pen.goto(x, y)
    pen.color(color)
    if fill:
        pen.begin_fill()
    pen.pendown()
    pen.forward(dx)
    pen.left(90)
    pen.forward(dy)
    pen.left(90)
    pen.forward(dx)
    pen.left(90)
    pen.forward(dy)
    if fill:
        pen.end_fill()
    pen.penup()


class Graphics:

    def __init__(self, nx: int, ny: int, ng: int, topbar: int = 100):
        self.nx = nx
        self.ny = ny
        self.ng = ng
        self.topbar = topbar

        self.screen = turtle.Screen()
        self.screen.clearscreen()

        self.screen.setup(width=self.nx, height=self.ny + self.topbar)
        self.screen.setworldcoordinates(0, 0, self.nx, self.ny + self.topbar)

        cv = self.screen.getcanvas()
        cv.adjustScrolls()

        self.background = '#D3D3D3'
        self.screen.bgcolor(self.background)
        # self.screen.bgpic('background.png')
        # cv.itemconfig(self.screen._bgpic, anchor="sw")
        self.screen.tracer(0)

        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.hideturtle()

        self.score_pen = turtle.Turtle()
        self.score_pen.hideturtle()
        self.score_pen.speed(0)
        self.score_pen.penup()
        self.score_pen.goto(self.nx // 2, self.ny)
        self.score_pen.pendown()

        self.add_grid()
        self.add_border()

        self.knights = {}
        self.previous_update = -10
        self.next_scoreboard_update = -1

    def add_grid(self):

        self.pen.color('#BDBDBD')
        self.pen.penup()
        self.pen.goto(0, 0)
        self.pen.setheading(90)
        self.pen.pendown()
        for i in range(self.nx // self.ng):
            self.pen.forward(self.ny)
            if i % 2 == 0:
                self.pen.right(90)
            else:
                self.pen.left(90)
            self.pen.forward(self.ng)
            if i % 2 == 0:
                self.pen.right(90)
            else:
                self.pen.left(90)

        self.pen.penup()
        self.pen.goto(0, 0)
        self.pen.setheading(0)
        self.pen.pendown()
        for i in range(self.ny // self.ng):
            self.pen.forward(self.nx)
            if i % 2 == 0:
                self.pen.left(90)
            else:
                self.pen.right(90)
            self.pen.forward(self.ng)
            if i % 2 == 0:
                self.pen.left(90)
            else:
                self.pen.right(90)

        self.pen.penup()

    def add_border(self):
        rectangle(self.pen, x=0, y=0, dx=self.nx, dy=self.ny, color='black')

    def add_obstacles(self, obstacles: dict):
        x = obstacles['x']
        y = obstacles['y']
        dx = obstacles['dx']
        self.pen.color('#2F4F4F')
        for i in range(len(x)):
            rectangle(self.pen,
                      x=x[i] - 0.5 * dx,
                      y=y[i] - 0.5 * dx,
                      dx=dx,
                      dy=dx,
                      color='#2F4F4F',
                      fill=True)

    def add_castles(self, castles: dict):
        dx = castles['dx']
        thickness = castles['thickness']
        star_size = int(castles['dx'] / 3)
        for team in ('red', 'blue'):
            params = castles[team]
            self.pen.color(team)
            self.pen.penup()
            d = params['direction']
            if d == 0:
                self.pen.goto(params['x'] + 0.5 * dx, params['y'] + 0.5 * dx)
                self.pen.setheading(180)
            elif d == 1:
                self.pen.goto(params['x'] - 0.5 * dx, params['y'] + 0.5 * dx)
                self.pen.setheading(270)
            elif d == 2:
                self.pen.goto(params['x'] - 0.5 * dx, params['y'] - 0.5 * dx)
                self.pen.setheading(0)
            elif d == 3:
                self.pen.goto(params['x'] + 0.5 * dx, params['y'] - 0.5 * dx)
                self.pen.setheading(90)
            self.pen.pendown()
            self.pen.begin_fill()
            self.pen.forward(dx)
            self.pen.left(90)
            self.pen.forward(dx)
            self.pen.left(90)
            self.pen.forward(dx)
            self.pen.left(90)
            self.pen.forward(thickness)
            self.pen.left(90)
            self.pen.forward(dx - thickness)
            self.pen.right(90)
            self.pen.forward(dx - (2 * thickness))
            self.pen.right(90)
            self.pen.forward(dx - thickness)
            self.pen.left(90)
            self.pen.forward(thickness)
            self.pen.end_fill()

            self.pen.penup()
            self.pen.goto(params['x'] - 0.5 * star_size,
                          params['y'] - 0.25 * star_size)
            self.pen.setheading(0)
            self.pen.pendown()
            self.pen.begin_fill()
            for i in range(5):
                self.pen.forward(star_size)
                self.pen.left(360 / 2.5)
            self.pen.end_fill()

    def add_fountains(self, fountains: dict):

        for team in ('red', 'blue'):
            params = fountains[team]
            self.pen.color('green')
            self.pen.penup()
            self.pen.goto(params['x'] - params['size'], params['y'])
            self.pen.pendown()
            self.pen.setheading(270)
            self.pen.circle(params['size'])
            self.pen.penup()
            self.pen.goto(params['x'], params['y'])
            self.pen.pendown()
            self.pen.setheading(0)
            self.pen.write("Fountain",
                           move=False,
                           align="center",
                           font=('Arial', 12, 'normal'))

    def add_gems(self, gems: dict):
        x = gems['x']
        y = gems['y']
        r = 10

        self.pen.color('orange')
        for i in range(len(x)):
            self.pen.penup()
            self.pen.goto(x[i], y[i])
            self.pen.pendown()
            self.pen.dot(r)

    def erase_gem(self, x: float, y: float):
        r = 10

        self.pen.color(self.background)
        self.pen.penup()
        self.pen.goto(x, y)
        self.pen.pendown()
        self.pen.dot(r)
        self.pen.penup()

    def initialize_scoreboard(self, knights: list, score: dict):
        self.pen.setheading(0)
        self.pen.color('black')
        self.pen.pensize(1)
        self.pen.penup()
        self.pen.goto(self.nx // 2 + 20, self.ny + self.topbar - 25)
        self.pen.pendown()
        self.pen.write("Time left =",
                       move=False,
                       align="right",
                       font=('Arial', 18, 'normal'))

        self.pen.penup()
        self.pen.goto(self.nx // 2 - 150, self.ny + 10)
        self.pen.pendown()
        self.pen.write('Gems:',
                       move=False,
                       align="center",
                       font=('Arial', 10, 'normal'))
        self.pen.penup()
        self.pen.goto(self.nx // 2 + 150, self.ny + 10)
        self.pen.pendown()
        self.pen.write('Gems:',
                       move=False,
                       align="center",
                       font=('Arial', 10, 'normal'))

        self.pen.penup()
        self.pen.goto(self.nx // 2, self.ny + 40)
        self.pen.pendown()
        self.pen.write(f"Round number {score['count']}",
                       move=False,
                       align="center",
                       font=('Arial', 18, 'normal'))

        self.pen.penup()
        self.pen.goto(self.nx // 2, self.ny + 10)
        self.pen.pendown()
        self.pen.write(f"{score['red']} - {score['blue']}",
                       move=False,
                       align="center",
                       font=('Arial', 18, 'normal'))

        red_knights = ['', '', '']
        blue_knights = ['', '', '']
        for knight in knights:
            if knight.team == 'red':
                red_knights[
                    knight.number] = f'{knight.name} - {knight.ai.creator}'
            else:
                blue_knights[
                    knight.number] = f'{knight.ai.creator} - {knight.name}'

        self.pen.color('red')
        self.pen.penup()
        self.pen.goto(self.nx // 2 - 330, self.ny + 10)
        self.pen.pendown()
        self.pen.write('\n\n'.join(red_knights[i] for i in range(3)),
                       move=False,
                       align='right',
                       font=('Arial', 10, 'normal'))
        self.pen.color('blue')
        self.pen.penup()
        self.pen.goto(self.nx // 2 + 330, self.ny + 10)
        self.pen.pendown()
        self.pen.write('\n\n'.join(blue_knights[i] for i in range(3)),
                       move=False,
                       align='left',
                       font=('Arial', 10, 'normal'))
        self.pen.penup()

    def update_scoreboard(self, t: float, knights: list, time_limit: float,
                          gems_found: dict):
        self.score_pen.clear()
        self.score_pen.setheading(0)

        self.score_pen.color('black')
        self.score_pen.penup()
        self.score_pen.goto(self.nx // 2 + 50, self.ny + self.topbar - 25)
        self.score_pen.pendown()
        self.score_pen.write(str(int(time_limit - t)),
                             move=False,
                             align="center",
                             font=('Arial', 18, 'normal'))

        self.score_pen.penup()
        self.score_pen.goto(self.nx // 2 - 120, self.ny + 10)
        self.score_pen.pendown()
        self.score_pen.write(str(gems_found['red']),
                             move=False,
                             align="center",
                             font=('Arial', 10, 'normal'))
        self.score_pen.penup()
        self.score_pen.goto(self.nx // 2 + 185, self.ny + 10)
        self.score_pen.pendown()
        self.score_pen.write(str(gems_found['blue']),
                             move=False,
                             align="center",
                             font=('Arial', 10, 'normal'))

        healthbar_dy = 15
        no_knight = ' ' * 126
        red_knights = [no_knight for i in range(3)]
        blue_knights = [no_knight for i in range(3)]
        for knight in knights:
            perc = knight.health / knight.max_health
            if knight.team == 'red':
                x = 0
            else:
                x = self.nx
            y = self.ny + 10 + ((2 - knight.number) * (healthbar_dy + 12))
            if perc > 0.5:
                fill = 'lime'
            elif perc < 0.2:
                fill = 'red'
            else:
                fill = 'gold'
            if knight.cooldown > 0:
                fill = 'cyan'
            plus_or_minus_one = (1 - (2 * (knight.team == 'blue')))
            rectangle(self.score_pen,
                      x=x + 1 * plus_or_minus_one,
                      y=y + 2,
                      dx=3 * knight.health * plus_or_minus_one,
                      dy=healthbar_dy,
                      color=fill,
                      fill=True)

            text = (f'attack={knight.attack} speed={int(knight.speed)} ' +
                    f'health={int(knight.health)} / {int(knight.max_health)}')
            padding = ' ' * (len(no_knight) - len(text))
            if knight.team == 'red':
                red_knights[knight.number] = text + padding
            else:
                blue_knights[knight.number] = padding + text

        one_text = '\n\n'.join(red_knights[i] + blue_knights[i]
                               for i in range(3))
        self.score_pen.penup()
        self.score_pen.goto(5, self.ny + 10)
        self.score_pen.color('black')
        self.score_pen.pendown()
        self.score_pen.write(one_text,
                             move=False,
                             align='left',
                             font=('Arial', 10, 'normal'))

    def update(self,
               t: float,
               knights: list,
               time_limit: float,
               gems_found: dict,
               show_messages: bool = False):
        self.next_scoreboard_update += 1
        if self.next_scoreboard_update % 15 == 0:
            self.next_scoreboard_update = 0
            self.update_scoreboard(t=t,
                                   knights=knights,
                                   time_limit=time_limit,
                                   gems_found=gems_found)
            if show_messages:
                for knight in knights:
                    if knight.ai.message is not None:
                        print(f'{knight.name} ({knight.ai.creator}) says: '
                              f'{knight.ai.message}')
        self.screen.update()

    def announce_winner(self, winner: str):
        self.pen.penup()
        self.pen.goto(self.nx // 2, self.ny // 2)
        self.pen.pendown()
        if winner is None:
            self.pen.color('black')
            self.pen.write("It's a draw",
                           move=False,
                           align="center",
                           font=('Arial', 100, 'normal'))
        else:
            print(winner, 'team wins!')
            self.pen.color(winner)
            self.pen.write(f"{winner} team wins!",
                           move=False,
                           align="center",
                           font=('Arial', 100, 'normal'))
        self.screen.update()
