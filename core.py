from collections import namedtuple



#
# We'll store player data in three different strucutres:
#  - PlayerGPAttributes: game play related attributes -- eg, things like speed, accelration, etc.
#      (basically, numeric stuff)
#  - PlayerMiscAttributes: all other player attributes -- eg, boost, program, date added, etc.
#  - Player: attributes searchable for auction house (team, position, ovr) and fields for two
#      structures above
#

# game play attributes keys
_PlayerGPAttributes = ['HT', 'WT', 'ADJUSTED OVR', 'OVR', 'SPD', 'STR', 'AGI', 'ACC', 'AWR',
                       'CAT', 'JMP', 'STA', 'INJ', 'TRU', 'ELU', 'BCV', 'STF', 'SPM', 'JKM',
                       'CAR', 'RTE', 'CIT', 'SPC', 'REL', 'THP', 'THA', 'TAS', 'TAM', 'TAD',
                       'RBK', 'RBS', 'RBF', 'PBK', 'PBS', 'PBF', 'IMB', 'TKL', 'HTP', 'PWM',
                       'FNM', 'BKS', 'PST', 'PLR', 'MAN', 'ZON', 'PRS', 'KIP', 'KIA', 'KRT',
                       'IMP', 'MOR', 'PAC', 'RNS', 'TOR', 'TOU', ]

# other attributes keys
_PlayerMiscAttributes = [ "PROGRAM", "BOOST", "DATE", 'DESCRIPTION OF CARD', 'CARDID']

# struct for each player's boosts (if applicable)
PlayerBoost = namedtuple("PlayerBoost", [ 'team', 'attribute', 'value' ])

# top level fields of Player class hold auction house searchable player characteristics.
# Everything else is in attributes field
Player = namedtuple("Player", ['name', 'display_name', 'program', 'position', 'team', 'ovr',
                               'type', 'auctionable', 'boosts', 'gp_attributes', 'misc_attributes' ])






class AuctionFilter(object):
    """
    A single auction house filter rule

    """
    def __init__(self, name=None, positions=None,
                 teams=None, min_ovr=None, max_ovr=None, types=None):
        self.name = name
        self.positions = positions
        self.teams = teams
        self.min_ovr = min_ovr
        self.max_ovr = max_ovr
        self.types = types

    def filter(self, universe):
        """
        Find players thatsatify this filter in given universe

        """

        good = []
        for player in universe:
          if player.auctionable == "Yes":
            if self.name is None or self.name in player.name:
              if self.min_ovr is None or player.ovr >= self.min_ovr:
                if self.max_ovr is None or player.ovr <= self.max_ovr:
                  if self.types is None or player.type in self.types:
                    if self.teams is None or player.team in self.teams:
                      if self.positions is None or player.position in self.positions:
                        good.append(player)

        return good

    def merge(self, other):
        """
        Naive merge of this filter with another..

        Does not perform any sort of logic

        """
        name = self.name
        teams = self.teams
        positions = self.positions
        min_ovr = self.min_ovr
        max_ovr = self.max_ovr
        types = self.types

        if name is None:
            name = other.name

        if teams is None:
            teams = other.teams

        if positions is None:
            positions = other.positions

        if min_ovr is None:
            min_ovr = other.min_ovr

        if max_ovr is None:
            max_ovr = other.max_ovr

        if types is None:
            types = other.types

        merged = self.__class__(name=name, teams=teams, positions=positions,
                                min_ovr=min_ovr, max_ovr=max_ovr, types=types)

        return merged

    def __repr__(self):
        s = "{}(".format(self.__class__.__name__)

        if self.name is not None:
            s += "name={}".format(self.name)

        if self.teams is not None:
            if self.name is not None:
                s += ", "

            if len(self.teams) < 4:
                s += "teams={}".format(self.teams)
            else:
                s += "{} teams".format(len(self.teams))

        if self.positions is not None:
            if len(self.positions) < 4:
                s += ", positions={}".format(self.positions)
            else:
                s += ", {} positions".format(len(self.positions))

        if self.min_ovr is not None:
            s += ", min_ovr={}".format(self.min_ovr)

        if self.max_ovr is not None:
            s += ", max_ovr={}".format(self.max_ovr)

        if self.types is not None:
            s += ", types={}".format(self.types)

        s += ")"

        return s
