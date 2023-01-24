def fight(knights, game_map, t):
    cooldown = 3  # 3 seconds
    combats = {}
    dead = []
    for k in knights:
        igrid = k.x // game_map.ng
        jgrid = k.y // game_map.ng
        key = f'{igrid},{jgrid}'
        if key not in combats:
            combats[key] = {k.team: [k]}
        elif k.team not in combats[key]:
            combats[key][k.team] = [k]
        else:
            combats[key][k.team].append(k)
    for key in combats:
        if set(combats[key]) == {'blue', 'red'}:
            blue_attack = sum([
                k.attack if k.cooldown == 0 else 0
                for k in combats[key]['blue']
            ])
            red_attack = sum([
                k.attack if k.cooldown == 0 else 0 for k in combats[key]['red']
            ])
            for k in combats[key]['blue']:
                k.health -= int(red_attack / len(combats[key]['blue']))
                if k.health <= 0:
                    dead.append(k)
                if k.cooldown == 0:
                    k.cooldown = cooldown
            for k in combats[key]['red']:
                k.health -= int(blue_attack / len(combats[key]['red']))
                if k.health <= 0:
                    dead.append(k)
                if k.cooldown == 0:
                    k.cooldown = cooldown
    return dead
