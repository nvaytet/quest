from pathlib import Path
from itertools import combinations
import numpy as np
from random import shuffle
import yaml
import shutil
from match import Match
import turtle


class Participant:

    def __init__(self,
                 name: str,
                 knights: dict,
                 rounds_won: int = 0,
                 matches_won: int = 0):
        self.name = name
        self.knights = knights
        self.rounds_won = rounds_won
        self.matches_won = matches_won

    def to_dict(self) -> dict:
        return {'rounds_won': self.rounds_won, 'matches_won': self.matches_won}


def make_team(team):
    creator = list(team.values())[0]().creator
    return {creator: Participant(name=creator, knights=team)}


class Manager:

    def __init__(self, *participants):

        self.participants = {}
        for team in participants:
            creator = list(team.values())[0]().creator
            self.participants[creator] = Participant(name=creator,
                                                     knights=team)

        self.matches = []
        self.phase = 0
        self.filename = Path("tournament.yaml")

        if self.filename.exists():
            self.load()
        else:
            self.make_tournament()
            self.save()

    def make_tournament(self):
        # Phase 1
        matches = list(combinations(self.participants.keys(), 2))
        shuffle(matches)
        for i, match in enumerate(matches):
            red = match[0]
            blue = match[1]
            self.matches.append(
                Match(red_team={red: self.participants[red]},
                      blue_team={blue: self.participants[blue]},
                      number=i + 1,
                      phase=1,
                      manager=self))
        # Phase 2
        n_per_round = 6
        matches_per_participant = len(self.participants) - 1
        match_list = list(self.participants.keys()) * matches_per_participant
        sets = []
        while len(match_list) > 0:
            possibles = list(set(match_list))
            this_round = []
            if len(possibles) < n_per_round:
                div = len(possibles) // 2
                red = possibles[:div]
                blue = possibles[div:]
                match_list.clear()
            else:
                for i in range(n_per_round):
                    ind = np.random.choice(range(len(possibles)))
                    this_round.append(possibles.pop(ind))
                red = set(this_round[:3])
                blue = set(this_round[3:])
            if (red not in sets) and (blue not in sets):
                self.matches.append(
                    Match(red_team={r: self.participants[r]
                                    for r in red},
                          blue_team={b: self.participants[b]
                                     for b in blue},
                          number=len(self.matches) + 1,
                          phase=2,
                          manager=self))

                sets += [red, blue]
                for name in this_round:
                    match_list.remove(name)

    def load(self):
        with open(self.filename) as f:
            data = yaml.load(f, Loader=yaml.loader.SafeLoader)
        for n, m in data['matches'].items():
            for r in m['rounds']:
                if r is not None:
                    for p in m[r]:
                        self.participants[p].rounds_won += 1
            if m['winner'] is not None:
                for p in m[m['winner']]:
                    self.participants[p].matches_won += 1

            self.matches.append(
                Match(red_team={r: self.participants[r]
                                for r in m['red']},
                      blue_team={b: self.participants[b]
                                 for b in m['blue']},
                      number=n,
                      phase=m['phase'],
                      rounds=m['rounds'],
                      manager=self,
                      winner=m['winner']))

    def save(self):
        out = {
            'participants':
            {name: p.to_dict()
             for name, p in self.participants.items()},
            'matches': {m.number: m.to_dict()
                        for m in self.matches}
        }
        if self.filename.exists():
            shutil.copyfile(self.filename, 'backup.yaml')
        with open(self.filename, 'w') as f:
            yaml.dump(out, f, sort_keys=False, default_flow_style=False)

    def next_match(self):
        for m in self.matches:
            if not m.is_complete():
                return m

    def show_scores(self):

        longest_name = len(max(self.participants.keys(), key=len))
        header = '   Rounds  Matches'
        title = " SCORES "
        diff = (4 + len(header) + longest_name - len(title)) // 2
        text = ('=' * diff) + title + ('=' * diff) + '\n'
        text += (' ' * (longest_name + 4)) + header + '\n'
        for n, (k, v) in enumerate(
                sorted(self.participants.items(),
                       key=lambda item:
                       (item[1].rounds_won, item[1].matches_won),
                       reverse=True)):
            text += (str(n + 1).rjust(2) + '. ' + k.ljust(longest_name) +
                     ':  ' + str(v.rounds_won).rjust(6) + '  ' +
                     str(v.matches_won).rjust(7) + '\n')
        next_match = self.next_match()
        if next_match is not None:
            for i, m in enumerate(self.matches):
                if m.phase == 2:
                    phase_1_length = i
                    break
            phase_2_length = len(self.matches) - phase_1_length
            number_in_phase = next_match.number
            ntot_phase = phase_1_length
            if next_match.phase == 2:
                next_match.number -= phase_1_length
                ntot_phase = phase_2_length
            text += (f'\nNext match is: Phase {next_match.phase} '
                     f'({number_in_phase}/{ntot_phase})\n'
                     f'{next_match.to_string()}\n')
        screen = turtle.Screen()
        screen.clearscreen()
        screen.tracer(0)
        pen = turtle.Turtle()
        pen.speed(0)
        pen.hideturtle()
        pen.penup()
        pen.goto(500, 300)
        pen.pendown()
        pen.write(text, move=False, align="left", font=('Arial', 32, 'normal'))
        pen.penup()
