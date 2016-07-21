from ..team import Team, _allowable_player_positions, _team_positions
import util as _opt_util
import random, copy

def optimize(population_size, players, obj_func, num_evolutions=1000, include_individuals=None, 
             constrained_players=None, verbose=False):

    if constrained_players is None:
        constraned_players = {}

    preprocessed_player_db = _opt_util.pre_process_database(players, constrained_players=constrained_players)

    if include_individuals is not None:
        population = copy.deepcopy(include_individuals)
        population.extend(create_population(preprocessed_player_db, population_size - len(include_individuals)))
    else:
        population = create_population(preprocessed_player_db, population_size)

    obj_values = [ obj_func(t) for t in population ]
    mean_obj = _mean(obj_values)
    max_obj = max(obj_values)
    prior_max = max_obj
    
    if verbose:
        print("initial population: mean={:.2f}, max={:.2f}".format(mean_obj, max_obj))

    for istep in range(num_evolutions):
        population = evolve_one_step(population, preprocessed_player_db, obj_func)

        obj_values = [ obj_func(t) for t in population ]
        mean_obj = _mean(obj_values)
        max_obj = max(obj_values)
        
        if verbose:
            print("iteration[{}]: population: mean={:.2f}, max={:.2f}".format(istep, mean_obj, max_obj))

        prior_max = max_obj
        old_population = population

    best_res = max(population, key=obj_func)

    misc_res = dict()
    misc_res['population'] = population
    
    return best_res, misc_res





def _choose_random_player(player_db, team, roster_position, verbose=False):
    """
    Choose a random player that is elibigle for roster_position
    
    """ 


    possible_players_to_add = player_db[roster_position]

    # now drop players already on roster
    # we only do this if there is more than 1 possible player to add.  If there is only 1 player to add..
    # that means this position is constrained to just 1 player so he must already be on the team! 
    if len(possible_players_to_add) > 1:
        possible_players_to_add = [ p for p in possible_players_to_add if not team.contains(p) ]

    if verbose:
        print("Choosing random player for {}: "
                "{} possible players".format(roster_position, len(possible_players_to_add)))
    # and pick random player 
    player_to_add = random.choice(possible_players_to_add)

    return player_to_add


def create_individual(player_db, verbose=False):
    """ 
    Create one random individual (team)

    Parameters
    top_ovr_filters:    if not None, only consider top n players (rated by ovr) for
                        each position
                    
    include_boosted_players:    always include players with boost, even if they are 
                        not in *top_ovr_filters* list

    """

    team = Team()

    for roster_position in _team_positions:

        player_to_add = _choose_random_player(player_db, team, roster_position,  verbose=verbose)
        
        if verbose:
            print("Adding {}: {}".format(roster_position, player_to_add.display_name))

        team.set_position(roster_position, player_to_add)

    return team

def create_population(player_db, num_individuals, include_indivuals=None, verbose=False):
    """
    Create population of individuals

    include_indivuals is list of individuals that must be added to this population

    """
    if include_indivuals is None:
        include_indivuals = []

    population = []
    for i in range(num_individuals - len(include_indivuals)):
        new_individual = create_individual(player_db)
        population.append(new_individual)
    
    population.extend(include_indivuals)

    return population

def combine_individuals(mother, father, verbose=False):
    """
    Breed two individuals...
    """

    while True:
        try:
            child = Team()

            for position in _team_positions:
                parent = random.choice([mother, father])
                player_to_add = parent.roster[position]

                if player_to_add in child.roster.values():
                    if parent is mother:
                        parent = father
                    else:
                        parent = mother
                    
                    player_to_add = parent.roster[position]

                if verbose:
                    if parent is mother:
                        parent_str = "mother"
                    else:
                        parent_str = "father"

                    print("Adding {}: {} [ from {} ]".format(position, player_to_add.display_name, parent_str))
            
                child.set_position(position, player_to_add)
        
        except ValueError:
            print("oops.. couldn't combine, trying again")
            continue
        
        return child


def mutate_individual(team, player_db, mutation_probability=.5, mutation_rate=.1, verbose=False):
    
    if random.random() < mutation_probability:
        team = copy.deepcopy(team)

        if verbose:
            print("Mutating!!")
        
        for roster_position in team.roster.keys():
            if random.random() < mutation_rate:

                player_to_add = _choose_random_player(player_db, team, roster_position)
                if verbose:
                    print("Mutating position {}: {}".format(roster_position, player_to_add.display_name))
                
                # player may be the same if this position is constrained to just one possible player
                if player_to_add.display_name != team.roster[roster_position].display_name:
                    team.set_position(roster_position, player_to_add)

    return team



def evolve_one_step(population, player_db, obj_func, mutation_probabiliy=.5, mutation_rate=.1,
                    keep_top_pct=.2, mutate_pct=.5, verbose=False):
    """
    Evolve population one step

    """
    obj_values = [ obj_func(team) for team in population ]

    keep_top_count = int(len(population) * keep_top_pct)
    mutate_count = int(len(population) * mutate_pct)
    combine_count = len(population) - keep_top_count - mutate_count
    
    if combine_count < 0:
        raise ValueError("keep_top_pct and mutate_pct must sum to less than 1.0")

    # keep any top individuals
    if keep_top_count > 0:
        if verbose:
            print("Keeping top {} individuals".format(keep_top_count))

        population_values = zip(population, obj_values)
        population_values = sorted(population_values, key=lambda x: x[1], reverse=True)
        
        top_individuals = [ pv[0] for pv in population_values[:keep_top_count] ]
    else:
        top_individuals = []

    
    #
    # mutate some
    #
    if verbose:
        print("Mutating {} individuals".format(mutate_count))

    mutated_individuals = []

    for i in range(mutate_count):
        individual_to_mutate = random.choice(population)
        new_individual = mutate_individual(individual_to_mutate, player_db)
        mutated_individuals.append(new_individual)
    
    #
    # and combine the rest...?
    #
    if verbose:
        print("Breeding for {} individuals".format(combine_count))

    breeded_individuals = []
    for i in range(combine_count):
        mother = random.choice(population)
        father = random.choice(population)

        while mother is father:
            father = random.choice(population)

        new_individual = combine_individuals(mother, father)
        breeded_individuals.append(new_individual)

    
    new_population = top_individuals + mutated_individuals + breeded_individuals
    return new_population



def _mean(values):

    count = len(values)
    total = sum(values)

    mean = float(total) / count

    return mean

