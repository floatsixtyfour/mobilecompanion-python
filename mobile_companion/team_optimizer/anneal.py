import random, math, copy
from ..team import _allowable_player_positions
import util as _opt_util

def optimize(team, players, obj_func, T_min=.0001, T_alpha=.9995, T=1.0,
             candidate_roster_positions=None, constrained_players=None, verbose=False):

    player_db = _opt_util.pre_process_database(players, constrained_players=constrained_players)

    if candidate_roster_positions is None:
        candidate_roster_positions = team.roster.keys()
    
    nsteps = 200

    original_obj = obj_func(team)
    best_obj = original_obj
    best_team = team

    iter = 0
    additional_runs = [ 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6, 7, 8]

    while T > T_min:
        current_obj = obj_func(team)

        new_team = _random_step(team, player_db, candidate_roster_positions)

        # allow multiple moves occaisonaly
        for i in range(random.choice(additional_runs)):
            new_team = _random_step(new_team, player_db, candidate_roster_positions)


        new_obj = obj_func(new_team)
        obj_improvement = new_obj - current_obj

        if obj_improvement > 0:
            acceptance_prob = 1.0
        else:
            acceptance_prob = math.exp(obj_improvement / T)

        if verbose:
            print("Iteration[{}, T={:.2f}]: current obj={:.3f}, "
                  "new obj={:.3f}, imp={:.3f}, prob={:.4%}".format(iter, T, current_obj, new_obj, 
                  obj_improvement, acceptance_prob))

        if verbose:
            #print("Acceptance prob = {}".format(acceptance_prob))
            pass

        if random.random() < acceptance_prob:
            team = new_team

            if new_obj > best_obj:
                best_obj = new_obj
                best_team = new_team

        iter += 1
        T = T * T_alpha

    return best_team

def _random_step(team, player_db, candidate_roster_positions=None, verbose=False, debug=False):
    """
    Find single best step to take

    candidate_roster_position is list of roster positions that we are allowed to change
    
    """
    team = copy.deepcopy(team)

    if candidate_roster_positions is None:
        candidate_roster_positions = team.roster.keys()

    roster_position = random.choice(candidate_roster_positions)

    possible_players_to_add = player_db[roster_position]

    # now drop players already on roster
    # we only do this if there is more than 1 possible player to add.  If there is only 1 player to add..
    # that means this position is constrained to just 1 player so he must already be on the team! 
    if len(possible_players_to_add) > 1:
        possible_players_to_add = [ p for p in possible_players_to_add if p not in team.roster.values() ]

    # and pick random player 
    swap_player = random.choice(possible_players_to_add)

    if verbose:
        print("replacing {} with {}".format(team.roster[roster_position], swap_player))

    team.set_position(roster_position, swap_player)

    return team