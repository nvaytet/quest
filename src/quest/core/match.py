# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations
from typing import Dict, Literal, Optional, TYPE_CHECKING

from .engine import Engine
if TYPE_CHECKING:
    from .manager import Manager, Participant


class Match:

    def __init__(self,
                 red_team: Dict[str, Participant],
                 blue_team: Dict[str, Participant],
                 number: int = 1,
                 phase: int = 1,
                 rounds: Optional[int] = None,
                 manager: Optional[Manager] = None,
                 winner: Optional[str] = None,
                 best_of: int = 3,
                 game_mode: Literal['king', 'flag'] = 'king'):
        self.red_team = red_team
        self.blue_team = blue_team
        self.number = number
        self.rounds = [] if rounds is None else rounds
        self.phase = phase
        self.manager = manager
        self.best_of = best_of
        self.first_to = self.best_of // 2 + 1
        self.match_winner = winner
        self.game_mode = game_mode

    def to_dict(self) -> dict:
        return {
            'phase': self.phase,
            'red': list(self.red_team.keys()),
            'blue': list(self.blue_team.keys()),
            'rounds': self.rounds,
            'number': self.number,
            'winner': self.match_winner
        }

    def to_string(self) -> str:
        return (f'red={list(self.red_team.keys())} VS '
                f'blue={list(self.blue_team.keys())}')

    def update_scores(self, winner: str):
        self.rounds.append(winner)
        if winner == 'red':
            for p in self.red_team.values():
                p.rounds_won += 1
        elif winner == 'blue':
            for p in self.blue_team.values():
                p.rounds_won += 1

    @property
    def score(self) -> dict:
        s = {'red': 0, 'blue': 0, 'count': len(self.rounds) + 1}
        for r in self.rounds:
            if r is not None:
                s[r] += 1
        return s

    def is_complete(self) -> bool:
        return (self.match_winner
                is not None) or (not (len(self.rounds) < self.best_of))

    def update_winner(self, winning_team: str):
        self.match_winner = winning_team
        if winning_team == 'red':
            for p in self.red_team.values():
                p.matches_won += 1
        elif winning_team == 'blue':
            for p in self.blue_team.values():
                p.matches_won += 1

    def play(self, speedup: int = 1, safe: bool = False, show_messages: bool = False):
        for n in range(len(self.rounds), self.best_of):

            if self.phase == 1:
                red = list(self.red_team.keys())[0]
                self.red_team[red].knights.reset_team()
                blue = list(self.blue_team.keys())[0]
                self.blue_team[blue].knights.reset_team()
                red_team = [(k, v) for k, v in self.red_team[red].knights.items()]
                blue_team = [(k, v) for k, v in self.blue_team[blue].knights.items()]
            else:
                red_team = []
                for p in self.red_team.values():
                    name = list(p.knights.keys())[0]
                    red_team.append((name, p.knights[name]))
                blue_team = []
                for p in self.blue_team.values():
                    name = list(p.knights.keys())[0]
                    blue_team.append((name, p.knights[name]))

            engine = Engine(score=self.score,
                            red_team=red_team,
                            blue_team=blue_team,
                            speedup=speedup,
                            show_messages=show_messages,
                            game_mode=self.game_mode)
            winner = engine.run(safe=safe)
            self.update_scores(winner)

            score = self.score
            a_team_has_won = False
            for team in ('red', 'blue'):
                if score[team] == self.first_to:
                    self.update_winner(team)
                    a_team_has_won = True
            if self.manager is not None:
                self.manager.save()
            if a_team_has_won:
                return

            input(f"Current score: red={score['red']} "
                  f"blue={score['blue']}. Start next round")

        score = self.score
        if score['red'] > score['blue']:
            self.update_winner('red')
        if score['blue'] > score['red']:
            self.update_winner('blue')
