from functools import partial
import numpy as np
import time

from game_map import Map
from graphics import Graphics
from fight import fight
from knight import Knight
from ai import BaseAI


def make_properties_dict(knight):
    return {
        'name': knight.name,
        'x': knight.x,
        'y': knight.y,
        'position': knight.position,
        'attack': knight.attack,
        'health': knight.health,
        'speed': knight.speed,
        'heading': knight.heading,
        'vector': knight.vector,
        'cooldown': knight.cooldown,
        'view_radius': knight.view_radius,
        'max_health': knight.max_health,
        'message': knight.ai.message,
        'team': knight.team,
        'kind': knight.ai.kind
    }


class Engine:

    def __init__(self,
                 score: dict,
                 red_team: list,
                 blue_team: list,
                 speedup: int = 1,
                 show_messages: bool = False):

        self.ng = 32
        self.nx = self.ng * 56
        self.ny = self.ng * 30
        self.graphics = Graphics(nx=self.nx, ny=self.ny, ng=self.ng)
        self.map = Map(nx=self.nx, ny=self.ny, ng=self.ng)
        self.speedup = int(speedup)
        self._show_messages = show_messages
        self._gems_found = {'red': 0, 'blue': 0}

        self.graphics.add_obstacles(self.map._obstacles)
        self.graphics.add_castles(self.map._castles)
        self.graphics.add_fountains(self.map._fountains)
        self.graphics.add_gems(self.map._gems)

        team_knights = {'red': red_team, 'blue': blue_team}
        self.team_counts = {
            'red': len(team_knights['red']),
            'blue': len(team_knights['blue'])
        }

        self.knights = []
        for team, groups in team_knights.items():
            for n, group in enumerate(groups):
                name, ai = group
                self.knights.append(
                    Knight(x=self.map._castles[team]['x'] +
                           self.map._castles['dx'] * 0.6 *
                           (1 - 2.0 * (int(team == 'blue'))),
                           y=int(self.map._castles[team]['y'] -
                                 0.5 * self.map._castles['dx'] +
                                 (n * 0.5 * self.map._castles['dx'])),
                           heading=180 - (180 * int(team == 'red')),
                           name=name,
                           team=team,
                           castle=self.map._castles[team],
                           fountain=self.map._fountains[team],
                           number=n,
                           AI=ai))
            # Add a king
            king = Knight(x=self.map._castles[team]['x'],
                          y=self.map._castles[team]['y'],
                          heading=0,
                          name='King',
                          team=team,
                          castle=self.map._castles[team],
                          fountain=self.map._fountains[team],
                          number=n + 1,
                          AI=partial(BaseAI, kind='king', creator=''))
            # king.ai.stop = True
            self.knights.append(king)

        self.graphics.initialize_scoreboard(knights=self.knights, score=score)

    def get_local_map(self, x: float, y: float, radius: float) -> np.ndarray:
        local_map = np.full((2 * radius + 1, 2 * radius + 1), -2)
        xmin = max(x - radius, 0)
        xmax = min(x + radius + 1, self.nx)
        ymin = max(y - radius, 0)
        ymax = min(y + radius + 1, self.ny)
        temp_map = self.map.array[xmin:xmax, ymin:ymax].copy()
        xm, ym = np.meshgrid(np.arange(xmin, xmax),
                             np.arange(ymin, ymax),
                             indexing='ij')
        dist_map = np.sqrt((xm - x)**2 + (ym - y)**2)
        invalid = dist_map > radius
        temp_map[invalid] = -1
        local_map[(xmin - x + radius):(xmax - x + radius),
                  (ymin - y + radius):(ymax - y + radius)] = temp_map
        return temp_map, local_map

    def get_info(self, knight: Knight, friends_as_dict: bool = False):
        r = knight.view_radius
        local_map, constant_shape_map = self.get_local_map(x=knight.x,
                                                           y=knight.y,
                                                           radius=r)
        friends = []
        enemies = []
        for k in self.knights:
            props = make_properties_dict(k)
            if (k.team != knight.team):
                del props['message']
                dist = knight.get_distance(k.position)
                if dist < knight.view_radius:
                    enemies.append(props)
            elif k.id != knight.id:
                if friends_as_dict:
                    friends.append(props)
                else:
                    friends.append(k)
            else:
                my_props = props

        flags = {}
        for team in ('red', 'blue'):
            pos = self.map._flags[team]
            dist = knight.get_distance(pos)
            if team == knight.team or dist < knight.view_radius:
                flags[team] = pos

        gems = {}
        gem_inds = np.where(local_map == 2)
        if len(gem_inds[0]) > 0:
            gems = {
                'x': gem_inds[0] + max(knight.x - r, 0),
                'y': gem_inds[1] + max(knight.y - r, 0)
            }

        return {
            'local_map': local_map,
            'constant_shape_map': constant_shape_map,
            'friends': friends,
            'enemies': enemies,
            'gems': gems,
            'flags': flags,
            'me': my_props,
            'fountain': self.map._fountains[knight.team]
        }

    def pickup_gem(self, x: float, y: float, team: str):
        kind_mapping = {0: ('attack', 2), 1: ('health', 4), 2: ('speed', 8)}
        kind = np.random.choice([0, 1, 2])
        bonus = np.random.random() * kind_mapping[kind][1]
        for k in self.knights:
            if k.team == team:
                if kind == 0:
                    k.attack += int(bonus) + 1
                elif kind == 1:
                    k.max_health += int(bonus) + 1
                elif kind == 2:
                    k.speed = min(k.speed + bonus, k.max_speed)
        self._gems_found[team] += 1

    def move(self, knight: Knight, t: float, dt: float, info: dict):

        if info['gems']:
            for x, y in zip(info['gems']['x'], info['gems']['y']):
                if (knight.get_distance((x, y)) <=
                    (knight.speed * dt)) and (abs(
                        abs(
                            knight.avatar.towards(x, y) -
                            knight.avatar.heading() - 180) - 180) < 10):
                    self.pickup_gem(x=x, y=y, team=knight.team)
                    self.map.array[x, y] = 0
                    self.graphics.erase_gem(x=x, y=y)
                    break

        pos = knight.ray_trace(dt=dt)
        above_xmin = np.amin(pos[0]) >= 0
        below_xmax = np.amax(pos[0]) < self.map.nx
        above_ymin = np.amin(pos[1]) >= 0
        below_ymax = np.amax(pos[1]) < self.map.ny
        xpos = np.minimum(np.maximum(pos[0], 0), self.map.nx - 1)
        ypos = np.minimum(np.maximum(pos[1], 0), self.map.ny - 1)
        no_obstacles = (np.sum(self.map.array[(xpos, ypos)] == 1)) == 0
        if (above_xmin and below_xmax and above_ymin and below_ymax
                and no_obstacles and (not knight.ai.stop)):
            knight.move(dt)

        opposing_team = 'red' if knight.team == 'blue' else 'blue'
        x, y = self.map._flags[opposing_team]
        dist_to_flag = knight.get_distance((x, y))
        if (((dist_to_flag <= (knight.speed * dt)) and (abs(
                abs(
                    knight.avatar.towards(x, y) - knight.avatar.heading() -
                    180) - 180) < 40)) or (dist_to_flag < 5)):
            return knight.team
        # no_guard = True
        # for k in self.knights:
        #     if (k.team == opposing_team) and (k.get_distance((x, y)) < 30):
        #         no_guard = False
        # if no_guard and (((dist_to_flag <= (knight.speed * dt)) and (abs(
        #         abs(
        #             knight.avatar.towards(x, y) - knight.avatar.heading() -
        #             180) - 180) < 40)) or (dist_to_flag < 5)):
        #     return knight.team

    def run(self, safe: bool = False, fps=30):

        t = 0
        time_limit = 180
        # dt = 1.0 * self.speedup
        dt = 1. / fps
        start_time = time.time()
        frame_times = np.linspace(dt, time_limit, int(time_limit / dt))
        dt *= self.speedup
        frame = 0
        while t < time_limit:
            t = (time.time() - start_time) * self.speedup
            if (frame < len(frame_times)) and (t >= frame_times[frame]):

                # dead_bodies = fight(knights=self.knights,
                #                     game_map=self.map,
                #                     t=t)

                for k in self.knights:
                    info = self.get_info(knight=k)
                    k.advance_dt(t=t, dt=dt, info=info)
                    info['friends'] = [
                        make_properties_dict(friend)
                        for friend in info['friends']
                    ]
                    k.execute_ai(t=t, dt=dt, info=info, safe=safe)
                    winner = self.move(knight=k, t=t, dt=dt, info=info)
                    if winner is not None:
                        self.graphics.announce_winner(winner)
                        return winner

                dead_bodies = fight(knights=self.knights,
                                    game_map=self.map,
                                    t=t)
                for k in dead_bodies:
                    k.avatar.color('black')
                    k.avatar_circle.clear()
                    self.knights.remove(k)
                    self.team_counts[k.team] -= 1
                if self.team_counts['red'] + self.team_counts['blue'] == 0:
                    winner = None
                    self.graphics.announce_winner(winner)
                    return winner
                for team in ('red', 'blue'):
                    if self.team_counts[team] == 0:
                        winner = 'red' if team == 'blue' else 'blue'
                        self.graphics.announce_winner(winner)
                        return winner

                self.graphics.update(t=t,
                                     knights=self.knights,
                                     time_limit=time_limit,
                                     gems_found=self._gems_found,
                                     show_messages=self._show_messages)
                frame += self.speedup

        self.graphics.announce_winner(None)
