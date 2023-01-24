from .manager import Manager
from ..players.templateAI import team as TemplateTeam

if __name__ == '__main__':

    manager = Manager(TemplateTeam, TemplateTeam, TemplateTeam, TemplateTeam,
                      TemplateTeam)

    while ((match := manager.next_match()) is not None):
        input(f'Next match is: {match.to_string()}')
        match.play(speedup=1, show_messages=False, safe=True)
        manager.show_scores()

    manager.show_scores()
    input('End of tournament!')
