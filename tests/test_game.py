# SPDX-License-Identifier: BSD-3-Clause

from quest.core.match import Match
from quest.core.manager import make_team
from quest.players.templateAI import team as TemplateTeam

match = Match(red_team=make_team(TemplateTeam),
              blue_team=make_team(TemplateTeam),
              best_of=3)

match.play(speedup=1, show_messages=False, mode='king')
