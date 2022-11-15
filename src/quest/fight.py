def fight(knights, game_map):
    cooldown = 50
    combats = {}
    dead = []
    for k in knights:
        if k.cooldown == 0:
            igrid = k.x // game_map.ng
            jgrid = k.y // game_map.ng
            key = f'{igrid},{jgrid}'
            if key not in combats:
                combats[key] = {k.team: [k]}
            elif k.team not in combats[key]:
                combats[key][k.team] = [k]
            else:
                combats[key][k.team].append(k)
    print(combats)
    # input('preeeees')
    for key in combats:
        if set(combats[key]) == {'blue', 'red'}:
            print("Fight in cell", key)
            print(combats[key])
            blue_attack = sum([k.attack for k in combats[key]['blue']])
            red_attack = sum([k.attack for k in combats[key]['red']])
            for k in combats[key]['blue']:
                k.health -= red_attack
                if k.health <= 0:
                    dead.append(k)
                k.cooldown = cooldown
            for k in combats[key]['red']:
                k.health -= blue_attack
                if k.health <= 0:
                    dead.append(k)
                k.cooldown = cooldown
            print(dead)
            print(combats[key])
            # input('press key')
    return dead
