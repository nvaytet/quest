from pathlib import Path
from itertools import combinations
import numpy as np
from random import shuffle
import yaml
import shutil
from match import Match
import turtle


class Participant:

    def __init__(self, name, knights, rounds_won=0, matches_won=0):
        self.name = name
        self.knights = knights
        self.rounds_won = rounds_won
        self.matches_won = matches_won

    def to_dict(self):
        return {'rounds_won': self.rounds_won, 'matches_won': self.matches_won}


# with open('UserDetails.yaml', 'w') as f:
#     data = yaml.dump(user_details, f, sort_keys=False, default_flow_style=False)


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

        # file = Path(self.filename)
        if self.filename.exists():
            self.load()
        else:
            self.make_tournament()
            self.save()

    def make_tournament(self):
        # # Phase 1
        # matches = list(combinations(self.participants.keys(), 2))
        # shuffle(matches)
        # for i, match in enumerate(matches):
        #     red = match[0]
        #     blue = match[1]
        #     self.matches.append(
        #         Match(red_team={red: self.participants[red]},
        #               blue_team={blue: self.participants[blue]},
        #               number=i + 1,
        #               phase=1,
        #               manager=self))
        # Phase 2
        n_per_round = 6
        matches_per_participant = len(self.participants) - 1
        l = list(self.participants.keys()) * matches_per_participant
        sets = []
        second_phase = []
        while len(l) > 0:
            possibles = list(set(l))
            this_round = []
            if len(possibles) < n_per_round:
                div = len(possibles) // 2
                red = possibles[:div]
                blue = possibles[div:]
                l.clear()
            else:
                for i in range(n_per_round):
                    ind = np.random.choice(range(len(possibles)))
                    this_round.append(possibles.pop(ind))
                red = set(this_round[:3])
                blue = set(this_round[3:])
            if (red not in sets) and (blue not in sets):
                # second_phase.append([list(red), list(blue)])
                #             red = match[0]
                # blue = match[1]
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
                    l.remove(name)

    def load(self):
        # from yaml.loader import SafeLoader
        # Open the file and load the file
        with open(self.filename) as f:
            data = yaml.load(f, Loader=yaml.loader.SafeLoader)
        for n, m in data['matches'].items():
            for r in m['rounds']:
                if r is not None:
                    print(m[r])
                    for p in m[r]:
                        self.participants[p].rounds_won += 1
                    # self.participants[r].rounds_won += 1
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
            # self.participants
        # self.matches = list(data['matches'].values())

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
        # with open('score.txt', 'r') as f:
        #     scores = f.readlines()
        # participants = {}
        # for line in scores:
        #     final_score = line.split('|')[-1].split(':')
        #     red_team = final_score[2]
        #     red_score = final_score[3]
        #     blue_team = final_score[4]
        #     blue_score = final_score[5]
        #     red_victory = int(red_score > blue_score)
        #     blue_victory = int(blue_score > red_score)
        #     if red_team not in participants:
        #         participants[red_team] = {
        #             'rounds': red_score,
        #             'matches': red_victory
        #         }
        #     else:
        #         participants[red_team]['rounds'] += red_score
        #         participants[red_team]['matches'] += red_victory
        #     if blue_team not in participants:
        #         participants[blue_team] = {
        #             'rounds': blue_score,
        #             'matches': blue_victory
        #         }
        #     else:
        #         participants[blue_team]['rounds'] += blue_score
        #         participants[blue_team]['matches'] += blue_victory

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
        print(text)
        next_match = self.next_match()
        if next_match is not None:
            text += f'\nNext match is: {next_match.to_string()}\n'
        screen = turtle.Screen()
        screen.clearscreen()
        screen.tracer(0)
        pen = turtle.Turtle()
        pen.speed(0)
        pen.hideturtle()
        pen.penup()
        pen.goto(500, 700)
        pen.pendown()
        pen.write(text, move=False, align="left", font=('Arial', 18, 'normal'))
        pen.penup()


# def other():
#     first_phase = [[[match[0]] * 3, [match[1]] * 3] for match in matches]
#     with open(match_list_file, 'w') as f:
#         f.write('First phase\n')
#         for match in first_phase:
#             f.write(':'.join(match[0]) + ':' + ':'.join(match[1]) + '\n')
#     #         # f.write(f'{match[0]}:{match[1]}\n')

#     n_per_round = 6
#     matches_per_participant = len(participants) - 1

#     l = list(participants.keys()) * matches_per_participant
#     sets = []
#     second_phase = []
#     while len(l) > 0:
#         possibles = list(set(l))
#         this_round = []
#         # print('possibles', possibles)
#         if len(possibles) < n_per_round:
#             div = len(possibles) // 2
#             red = possibles[:div]
#             blue = possibles[div:]
#             l.clear()
#         else:
#             for i in range(n_per_round):
#                 ind = np.random.choice(range(len(possibles)))
#                 this_round.append(possibles.pop(ind))
#             red = set(this_round[:3])
#             blue = set(this_round[3:])
#         if (red not in sets) and (blue not in sets):
#             second_phase.append([list(red), list(blue)])
#             sets += [red, blue]
#             for name in this_round:
#                 l.remove(name)

#     match_list_file = Path("match_list.txt")
#     if match_list_file.exists():
#         with open(match_list_file, 'r') as f:
#             matches = f.readlines()
#         n = 0
#         count = True
#         match_list = []
#         for match in matches:
#             if ':' in match:
#                 li = match.strip().split(':')
#                 match_list.append([li[:3], li[3:]])
#                 if count:
#                     n += 1
#             if 'Second phase' in match:
#                 count = False
#         return match_list, n
#     else:
#         matches = list(combinations(participants.keys(), 2))
#         shuffle(matches)
#         first_phase = [[[match[0]] * 3, [match[1]] * 3] for match in matches]
#         with open(match_list_file, 'w') as f:
#             f.write('First phase\n')
#             for match in first_phase:
#                 f.write(':'.join(match[0]) + ':' + ':'.join(match[1]) + '\n')
#         #         # f.write(f'{match[0]}:{match[1]}\n')

#         n_per_round = 6
#         matches_per_participant = len(participants) - 1

#         l = list(participants.keys()) * matches_per_participant
#         sets = []
#         second_phase = []
#         while len(l) > 0:
#             possibles = list(set(l))
#             this_round = []
#             # print('possibles', possibles)
#             if len(possibles) < n_per_round:
#                 div = len(possibles) // 2
#                 red = possibles[:div]
#                 blue = possibles[div:]
#                 l.clear()
#             else:
#                 for i in range(n_per_round):
#                     ind = np.random.choice(range(len(possibles)))
#                     this_round.append(possibles.pop(ind))
#                 red = set(this_round[:3])
#                 blue = set(this_round[3:])
#             if (red not in sets) and (blue not in sets):
#                 second_phase.append([list(red), list(blue)])
#                 sets += [red, blue]
#                 for name in this_round:
#                     l.remove(name)
#         with open(match_list_file, 'a') as f:
#             f.write('Second phase\n')
#             for match in second_phase:
#                 f.write(
#                     ':'.join([item for sublist in match
#                               for item in sublist]) + '\n')

#         return first_phase + second_phase, len(first_phase)

#         tree = ET.parse('score.xml')
#         root = tree.getroot()

#         print()