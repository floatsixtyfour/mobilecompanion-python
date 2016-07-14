import copy
from ..team import _allowable_player_positions

def best_swap(team, players, calculator, verbose=False):
    res_rounded = dict()
    res_raw = dict()

    player_score, team_score  = calculator.calculate(team)
    base_score = team_score['overall']
    base_score = team_score['offense']
    roster = team.roster

    for roster_position in roster.keys():
        cur_team = copy.deepcopy(team)
        allowable_player_positions = _allowable_player_positions[roster_position]
        possible_swaps = [ p for p in players if p.position in allowable_player_positions ]

        if verbose:
            print("Checking swaps for {} {} "
                  "[ {} players ]".format(roster_position,
                                          allowable_player_positions, len(possible_swaps)))

        # only check top 50 for now
        possible_swaps = sorted(possible_swaps, key=lambda x: x.ovr, reverse=True)[:10000]

        for possible_swap_player in possible_swaps:
            if possible_swap_player.name in [ p.name for p in team.roster.values() ]:
                if verbose:
                    print("Skipping existing player: {}".format(possible_swap_player.display_name))
                continue

            cur_team.set_position(roster_position, possible_swap_player)
            cur_ovr = calculator.calculate(cur_team)[1]['offense']

            indx = (roster_position, possible_swap_player.display_name)
            res_rounded[indx] = cur_ovr['rounded'] - base_score['rounded']
            res_raw[indx] = cur_ovr['raw'] - base_score['raw']

    return res_raw, res_rounded
