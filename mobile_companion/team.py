"""
Structure for storing teams

"""
import os

# mapping of roster positions to allowable players
_allowable_player_positions = dict(C=['C'], FB=['HB', 'FB'], HB=['HB'],
                                   LG=['OG'], RG=['OG'], LT=['OT'], RT=['OT'],
                                   QB=['QB'], TE=['TE'], WR1=['WR'], WR2=['WR'],
                                   SLOT=['WR', 'TE'],
                                   CB1=['CB'], CB2=['CB'], FS=['S'], SS=['S'],
                                   NICKEL=['CB', 'S'], DIME=['CB', 'S'],
                                   LOLB=['LB'], MLB=['MLB'], MLB34=['LB', 'MLB'],
                                   ROLB=['LB'],
                                   LE=['DE'], DT=['DT'], DT43=['DT'], RE=['DE'],
                                   K=['K'], KR=['KR'], P=['P'], PR=['PR'])

# roster positions on team
_team_positions_offense = [ 'C', 'FB', 'HB', 'LG', 'RG',
                            'LT', 'RT', 'QB',
                            'TE', 'WR1', 'WR2', 'SLOT' ]

_team_positions_defense = ['CB1', 'CB2', 'FS', 'SS',
                           'NICKEL', 'DIME',
                           'LOLB', 'MLB', 'MLB34', 'ROLB',
                           'LE', 'DT', 'DT43', 'RE' ]

_team_positions_special = ['K', 'KR', 'P', 'PR']

_team_positions = (_team_positions_offense + _team_positions_defense +
                   _team_positions_special)

class Team(object):
    """
    Roster of players
    """

    def __init__(self, name=None):
        self.name = name
        self.roster = dict()

    def set_position(self, roster_position, player):
        allowable_positions = _allowable_player_positions[roster_position]

        if player.position not in allowable_positions:
            raise ValueError("{} [{}] not allowable for {}.  Allowable positions "
                             "are: {}".format(player.display_name, player.position,
                                              roster_position, allowable_positions))

        if self.contains(player):
            raise ValueError("{} is already on roster".format(player.display_name))

        self.roster[roster_position] = player

    def contains(self, player):
        """
        Check if a player is already on a team
        """

        res = player.name in [ p.name for p in self.roster.values() ]
        return res

        

    @property
    def offense(self):
        """
        dict of offensive players (this is a copy ony)

        """
        roster = self.roster
        players = { pos: roster[pos] for pos in _team_positions_offense }

        return players

    @property
    def defense(self):
        """
        dict of defensive players (this is a copy ony)

        """
        roster = self.roster
        players = { pos: roster[pos] for pos in _team_positions_defense }

        return players

    @property
    def special(self):
        """
        dict of special teams players (this is a copy ony)

        """
        roster = self.roster
        players = { pos: roster[pos] for pos in _team_positions_special }

        return players


    @staticmethod
    def load(team_file, player_db):
        """
        Load existing team from file
        """

        if not os.path.exists(team_file):
            raise IOError("Team file not found: {}".format(team_file))

        team = Team()

        with open(team_file, 'r') as f:
            for line in f:
                if line.startswith("#"):
                    continue

                pos, player_name = line.strip().split('|')
                print(player_name)

                # look up player name in database...
                matched_player = [ p for p in player_db if p.display_name == player_name ]
                if len(matched_player) == 0:
                    raise ValueError("Unknown player: {}".format(player_name))
                elif len(matched_player) > 1:
                    raise ValueError("Multiple players match: {}!".format(player_name))
                else:
                    matched_player = matched_player[0]
                    team.set_position(pos, matched_player)

        # make sure all positions were filled...
        missing_positions = [ pos for pos in _team_positions if pos not in team.roster ]
        if len(missing_positions) > 0:
            raise ValueError("Following position(s) are missing: {}".format(missing_positions))

        return team
