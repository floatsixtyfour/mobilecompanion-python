"""
Calculators for various team & player overall metrics

"""

import os, csv, six
from collections import defaultdict

class Standard(object):
    """
    Standard overall rating
    """

    def __init__(self, weight_file=None):
        if weight_file is None:
            weight_file = 'standard_weights.dat'

        weights = self._load_weight_file(weight_file=weight_file)

        # separate out high/low/total from attribute weights
        high = dict()
        low = dict()
        total = dict()

        for roster_position in weights.keys():
            high[roster_position] = weights[roster_position].pop("HIGH")
            low[roster_position] = weights[roster_position].pop("LOW")
            total[roster_position] = weights[roster_position].pop("TOTAL")

        self.weights = weights
        self.high = high
        self.low = low
        self.total = total


    def calculate(self, team):
        # gather boosts first
        boosts = []
        for player in team.roster.values():
            boosts.extend(player.boosts)

        player_attributes = defaultdict(lambda : defaultdict(dict))
        team_attributes = defaultdict(lambda : defaultdict(float))

        #
        # calculate player ratings (raw & boosted) first
        #
        for roster_position, player in six.iteritems(team.roster):
            player_position = player.position
            position_weights = self.weights[player_position]
            for attribute, weight in six.iteritems(position_weights):
                player_attribute = player.gp_attributes[attribute]
                player_attributes['raw'][roster_position][attribute] = player_attribute
                player_attributes['boosted'][roster_position][attribute] = player_attribute

            # apply boosts
            for boost in boosts:
                if boost.team == "ALL" or boost.team == player.team:
                    player_attributes['boosted'][roster_position][boost.attribute] += boost.value

            # cap everything at 99 or original value
            for attribute in position_weights.keys():
                boosted_value = player_attributes['boosted'][roster_position][attribute]
                raw_value = player_attributes['raw'][roster_position][attribute]

                if boosted_value > 99:
                    if raw_value > 99:
                        new_value = min(raw_value, boosted_value)
                    else:
                        new_value = 99

                    player_attributes['boosted'][roster_position][attribute] = new_value


        #
        # and now values for team
        #

        # calcalute weighted score for each position and then sum (mean) them
        # later by offense, defense, special teams
        position_weighted_score = dict()

        # loop over "sub roster" (off, def, special) separately since each overall score
        # is an average of players in sub roster
        sub_roster_names = [ 'offense', 'defense', 'special' ]
        for sub_roster_name in sub_roster_names:
            sub_roster = getattr(team, sub_roster_name)

            for roster_position, player in six.iteritems(sub_roster):
                player_position = player.position
                position_weights = self.weights[player_position]
                position_weight_total = self.total[player_position]

                position_score_high = self.high[player_position]
                position_score_low = self.low[player_position]
                position_score_scaler = 100.0 / (position_score_high - position_score_low)

                player_weighted_score = 0.0
                for attribute, weight in six.iteritems(position_weights):
                    player_attribute_raw = player_attributes['raw'][roster_position][attribute]
                    player_attribute_boosted = player_attributes['boosted'][roster_position][attribute]
                    player_weighted_score += (player_attribute_boosted * weight)

                position_weighted_score[roster_position] = player_weighted_score / position_weight_total
                score_raw = (position_score_scaler *
                            (position_weighted_score[roster_position] - position_score_low))

                score_rounded = (position_score_scaler *
                                 (round(position_weighted_score[roster_position]) - position_score_low))

                team_attributes[sub_roster_name]['raw'] += score_raw
                team_attributes[sub_roster_name]['rounded'] += int(score_rounded)

                # also calculate values for overall here
                team_attributes["overall"]['raw'] += score_raw
                team_attributes["overall"]['rounded'] += int(score_rounded)

            # team scores are just averages
            team_attributes[sub_roster_name]['raw'] /= len(sub_roster)
            team_attributes[sub_roster_name]['rounded'] /= len(sub_roster)

        team_attributes["overall"]['raw'] /= len(team.roster)
        team_attributes["overall"]['rounded'] /= len(team.roster)

        # convert back to regular dictionaries
        player_attributes = dict(player_attributes)
        for k, v in six.iteritems(player_attributes):
            player_attributes[k] = dict(v)

        team_attributes = dict(team_attributes)
        for k, v in six.iteritems(team_attributes):
            team_attributes[k] = dict(v)

        return player_attributes, team_attributes



    def _load_weight_file(self, weight_file):
        if not os.path.exists(weight_file):
            raise IOError("Cannot find weight file: {}".format(weight_file))

        weights = defaultdict(dict)
        with open(weight_file, 'r') as f:
            reader = csv.reader(f)

            # headings first
            headings = next(reader)
            while headings[0].startswith("#"):
                headings = next(reader)

            headings = [ h.strip() for h in headings ]

            for irow, row in enumerate(reader):
                if row[0].startswith("#"):
                    continue

                roster_position = row[0]

                for icol, (col, value) in enumerate(zip(headings[1:], row[1:]), start=1):
                    try:
                        weights[roster_position][col] = float(value)
                    except:
                        raise ValueError("Error parsing value: {} "
                                         "[ row {}, col {}".format(value, irow, icol))

        weights = dict(weights)
        return weights