
def pre_process_database(player_db, top_ovr_filter=50, include_boosted_players=True, constrained_players=None):
    """
    Filter & transform database of players for efficiency

    top_ovr_filter: only keep top n players for each roster postition
    include_boosted_players: for inclusion of any players with boosts (these will
                             be in addition to top_ovr_filter)

    Filters player database and converts it into a more efficient format.  Ie, 
    creates dict of roster_positions -> list of eligble players based on
    _allowable_player_positions mapping

    """
    
    preprocessed_db = dict()

    for roster_position in _team_positions:
        allowable_player_positions = _allowable_player_positions[roster_position]
        possible_players_to_add = [ p for p in player_db if p.position in allowable_player_positions ]

        if top_ovr_filter is not None:

            # get list of boosted players now, before we filter
            if include_boosted_players:
                boosted_players = [ p for p in possible_players_to_add if len(p.boosts) > 0 ]
            
            # now filter
            possible_players_to_add = sorted(possible_players_to_add, key=lambda x: x.adjusted_ovr, reverse=True)
            possible_players_to_add = possible_players_to_add[:top_ovr_filter]

            # and add back boosted players if needed
            if include_boosted_players:
                boosted_players = [ p for p in boosted_players if p not in possible_players_to_add ]
                possible_players_to_add.extend(boosted_players)

        preprocessed_db[roster_position] = possible_players_to_add

    if constrained_players is not None:
        for roster_position, possible_players_to_add in constrained_players.iteritems():
            possible_players_to_add = [ p for p in player_db if p.display_name in possible_players_to_add ]
            preprocessed_db[roster_position] = possible_players_to_add

    return preprocessed_db
