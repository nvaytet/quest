# Quest

**AI coding challenge**

Two teams of 3 knights battle it out on a map riddled with obstacles and gems.

To win:

- Either: capture the enemy flag
- Or: kill all enemies

**Info**

A introduction on how to play can be found in the `docs` folder and there is a showcase in the `tests` folder.

**Install**

```
pip install .
```

**Run**

Create your own Team and import the knights or use the `TemplateTeam`.

```python
from quest.core.match import Match
from quest.core.manager import make_team
from quest.players.templateAI import team as TemplateTeam
match = Match(red_team=make_team(TemplateTeam),
              blue_team=make_team(TemplateTeam),
              best_of=3)
match.play(speedup=1, show_messages=False)
```
