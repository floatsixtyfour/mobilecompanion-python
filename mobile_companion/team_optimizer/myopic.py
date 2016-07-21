import copy
from ..team import _allowable_player_positions
import util as _opt_util


def optimize(team, players, obj_func, constrained_players=None, candidate_roster_positions=None, verbose=False):
    new_team = copy.deepcopy(team)

    player_db = _opt_util.pre_process_database(players, constrained_players=constrained_players)

    initial_obj = obj_func(new_team)
    if verbose:
        print("Initial objective value: {}".format(initial_obj))

    current_obj = initial_obj
    new_obj = current_obj

    iters = 0

    while ((iters < 20) and (new_obj - current_obj) > 0) or (iters == 0):
        if iters > 0:
            current_obj = new_obj

        next_move = _best_step(new_team, player_db, obj_func, 
                               candidate_roster_positions=candidate_roster_positions)

        if next_move is None:
            if verbose:
                print("No improving moves found on iteration {}".format(iters))
            break

        position_to_replace, player_to_add, new_obj = next_move

        if verbose:
            print("Swaping {} for {}, "
                "improvement: {}, new objective value: {}".format(team.roster[position_to_replace].display_name, 
                                                                  player_to_add, new_obj - current_obj, new_obj))
        
        new_team.set_position(position_to_replace, player_to_add)
        iters = iters + 1

    return new_team


def _best_step(team, player_db, obj_func, candidate_roster_positions=None, verbose=False, debug=False):
    """
    Find single best step to take

    candidate_roster_position is list of roster positions that we are allowed to change
    
    """
    
    original_score  = obj_func(team)

    if candidate_roster_positions is None:
        candidate_roster_positions = team.roster.keys()

    best_score = original_score
    best_swap = None
    current_score = original_score

    if verbose:
        print("Original objective value: {}".format(original_score))

    for roster_position in candidate_roster_positions:
        
        cur_team = copy.deepcopy(team)

        possible_swaps = player_db[roster_position]

        if verbose:
            print("Checking swaps for {}: "
                  "{} potential players".format(roster_position, len(possible_swaps)))

        for possible_swap_player in possible_swaps:
            if team.contains(possible_swap_player, exclude_position=roster_position):
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
                best_swap = (roster_position, possible_swap_player, best_score)

    return best_swap
