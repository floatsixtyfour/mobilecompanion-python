"""
Meta optimizer...

An attempt at using results from different optimizer to find an overall better result

"""
import genetic as TOG
import myopic as TOM
import anneal as TOA
import copy

def optimize(players, obj_func, initial_guess=None, verbose=False, constrained_players=None):
    """
    Meta optimization using various underlying optimizers
    """
    
    # we'll include various intermediate results in final GP for better diversity
    teams_to_include = []

    if initial_guess is not None:
        teams_to_include.append(initial_guess)


    # first try a small genetic opt to get a reasonable starting point
    best_team, res = TOG.optimize(5, players, obj_func=obj_func, num_evolutions=100, 
                                  constrained_players=constrained_players, include_individuals=teams_to_include)
    teams_to_include.append(copy.deepcopy(best_team))
    best_obj = obj_func(best_team)

    if verbose:
        print("Results from initial genetic opt: {}".format(best_obj))
    
    # now anneal that badboy
    best_team = TOA.optimize(best_team, players, obj_func=obj_func, constrained_players=constrained_players)
    teams_to_include.append(copy.deepcopy(best_team))
    best_obj = obj_func(best_team)
    
    if verbose:
        print("Results after annealing: {}".format(best_obj))

    # myopic too...
    best_team = TOM.optimize(best_team, players, obj_func=obj_func, constrained_players=constrained_players) 
    teams_to_include.append(copy.deepcopy(best_team))
    best_obj = obj_func(best_team)
    
    # include in large scale GP
    best_team, res = TOG.optimize(50, players, obj_func=obj_func, include_individuals=teams_to_include,
                                 constrained_players=constrained_players)
    best_obj = obj_func(best_team)

    if verbose:
        print("Results after 2nd pass genetic opt: {}".format(best_obj))

    # and final myopic
    best_team = TOM.optimize(best_team, players, obj_func=obj_func, constrained_players=constrained_players) 
    best_obj = obj_func(best_team)

    if verbose:
        print("Final result: {}".format(best_obj))

    return best_team, best_obj