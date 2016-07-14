import copy
from team import _allowable_player_positions

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


def best_step(team, players, obj_func, candidate_roster_positions=None, verbose=False, debug=False):
    """
    Find single best step to take

    candidate_roster_position is list of roster positions that we are allowed to change
    
    """
    
    original_score  = obj_func(team)

    if candidate_roster_positions is None:
        candidate_roster_positions = team.roster.keys()

    best_score = original_score
    best_swap = ()
    current_score = original_score

    if verbose:
        print("Original objective value: {}".format(original_score))

    for roster_position in candidate_roster_positions:
        
        cur_team = copy.deepcopy(team)
        allowable_player_positions = _allowable_player_positions[roster_position]
        possible_swaps = [ p for p in players if p.position in allowable_player_positions ]

        if verbose:
            print("Checking swaps for {} {} "
                  "[ {} players ]".format(roster_position,
                                          allowable_player_positions, len(possible_swaps)))

        # only check top 50 for now
        possible_swaps = sorted(possible_swaps, key=lambda x: x.ovr, reverse=False)[:10000]

        for possible_swap_player in possible_swaps:
            if possible_swap_player.name in [ p.name for p in team.roster.values() ]:
                if debug:
                    print("Skipping existing player: {}".format(possible_swap_player.display_name))
                continue

            cur_team.set_position(roster_position, possible_swap_player)
            current_score = obj_func(cur_team)

            if current_score > best_score:
                if verbose:
                    print("Found new best objective value: "
                          "{} [ {}:{} ]".format(current_score, roster_position, possible_swap_player.display_name))
                best_score = current_score
                best_swap = (roster_position, possible_swap_player)

    return best_swap
