def fight(knights, game_map, t):
    cooldown = 3  # 3 seconds
    combats = {}
    dead = []
    king_key = {'red': None, 'blue': None}
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
        if k.kind == 'king':
            king_key[k.team] = key
    for key in combats:
        if set(combats[key]) == {'blue', 'red'}:
            if key == king_key['blue']:
                blue_attack = max(
                    [k.attack if k.cooldown == 0 else 0 for k in combats[key]['blue']])
            else:
                blue_attack = sum(
                    [k.attack if k.cooldown == 0 else 0 for k in combats[key]['blue']])
            if key == king_key['red']:
                red_attack = max(
                    [k.attack if k.cooldown == 0 else 0 for k in combats[key]['red']])
            else:
                red_attack = sum(
                    [k.attack if k.cooldown == 0 else 0 for k in combats[key]['red']])
            for k in combats[key]['blue']:
                k.health = max(0,
                               k.health - int(red_attack / len(combats[key]['blue'])))
                if k.health <= 0:
                    dead.append(k)
                if k.cooldown == 0:
                    k.cooldown = cooldown
            for k in combats[key]['red']:
                k.health = max(0,
                               k.health - int(blue_attack / len(combats[key]['red'])))
                if k.health <= 0:
                    dead.append(k)
                if k.cooldown == 0:
                    k.cooldown = cooldown
    return dead
