import random, math, copy
from team import _allowable_player_positions

def anneal(team, players, obj_func, candidate_roster_positions=None, verbose=False):

    if candidate_roster_positions is None:
        candidate_roster_positions = team.roster.keys()
    
    nsteps = 200

    original_obj = obj_func(team)
    best_obj = original_obj
    best_team = team

    T_min = .0001
    T_alpha = .9995
    T = 1.0
    iter = 0
    additional_runs = [ 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6, 7, 8]

    while T > T_min:
        current_obj = obj_func(team)

        new_team = _random_step(team, players, candidate_roster_positions)

        # allow multiple moves occaisonaly
        for i in range(random.choice(additional_runs)):
            new_team = _random_step(new_team, players, candidate_roster_positions)


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
                print("New best obj!")
                best_obj = new_obj
                best_team = new_team

        iter += 1
        T = T * T_alpha

    return best_team

def _random_step(team, players, candidate_roster_positions=None, verbose=False, debug=False):
    """
    Find single best step to take

    candidate_roster_position is list of roster positions that we are allowed to change
    
    """
    team = copy.deepcopy(team)

    if candidate_roster_positions is None:
        candidate_roster_positions = team.roster.keys()

    roster_position = random.choice(candidate_roster_positions)

    allowable_player_positions = _allowable_player_positions[roster_position]
    possible_swaps = [ p for p in players if p.position in allowable_player_positions ]

    if verbose:
        print("Checking swaps for {} {} "
                "[ {} players ]".format(roster_position,
                                        allowable_player_positions, len(possible_swaps)))

    # only check top 50 for now
    potential_possible_swaps = sorted(possible_swaps, key=lambda x: x.ovr, reverse=True)[:50]
    
    # add players with boosts too!
    boosted_swaps = [ p for p in possible_swaps if len(p.boosts) > 0 and p not in potential_possible_swaps ]
    potential_possible_swaps.extend(boosted_swaps)
    

    # remove players already on roster
    possible_swaps = []
    for swap_player in potential_possible_swaps:
        if swap_player.name in [ p.name for p in team.roster.values() ]:
            if debug:
                print("Skipping existing player: {}".format(swap_player.display_name))
        else:
            possible_swaps.append(swap_player)

    # and pick random player 
    swap_player = random.choice(possible_swaps)

    if verbose:
        print("replacing {} with {}".format(team.roster[roster_position], swap_player))

    team.set_position(roster_position, swap_player)

    return team