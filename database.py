#
# Player database
#

from core import Player, PlayerBoost, _PlayerGPAttributes, _PlayerMiscAttributes
import os, csv

def import_database_csv(infile):
  """
  Import database from a CSV file

  """

  if not os.path.exists(infile):
    raise ValueError("Cannont find file: {}".format(infile))

  required_columns = [ 'PLAYER NAME', "FILTER NAME", "PROGRAM", "AUCTION", 'POS', 'TEAM', 'OVR', 'TYPE' ]
  required_columns += _PlayerGPAttributes
  required_columns += _PlayerMiscAttributes
  reader = csv.reader(open(infile))

  #
  # process header first
  #
  header = next(reader)

  # map required columns to what's in the file
  column_map = dict()

  for required_column in required_columns:
    if required_column not in header:
      raise ValueError("File does not contain required column: {}".format(required_column))

    column_map[required_column] = header.index(required_column)

  #
  # now read in all players
  #
  players = []
  for line in reader:
    player_display_name = line[column_map["PLAYER NAME"]]
    player_position = line[column_map["POS"]]
    player_team = line[column_map["TEAM"]]
    player_ovr = int(line[column_map["OVR"]])
    player_type = line[column_map["TYPE"]]
    player_name = line[column_map["FILTER NAME"]]
    player_program = line[column_map["PROGRAM"]]
    player_auctionable = line[column_map["AUCTION"]]
    player_adjusted_ovr = float(line[column_map["ADJUSTED OVR"]])

    # just concat all parts of name, ignoring what is first & last and normalize case
    player_name = " ".join(player_name.split(', ')).lower()

    # read in game play attributes
    gp_attributes = dict()
    for key in _PlayerGPAttributes:
        val = line[column_map[key]]

        # convert height into inches to make it numeric
        if key == "HT":
            ft, inches = val.split("'")
            inches = inches.replace('"', "")

            val = 12 * int(ft) + int(inches)

        gp_attributes[key] = float(val)

    misc_attributes = dict()
    for key in _PlayerMiscAttributes:
        misc_attributes[key] = line[column_map[key]]

    # deciper boosts..
    boosts_str = misc_attributes["BOOST"]
    player_boosts = []
    if boosts_str != "None":
        # boosts_str looks somethng like "ALL + 2 ZON -1 MAN"
        boosts_str = boosts_str.split()
        boost_team = boosts_str.pop(0)
        player_boosts = []
        while len(boosts_str):
            boost_value = float(boosts_str.pop(0))
            boost_attribute = boosts_str.pop(0)

            this_boost = PlayerBoost(team=boost_team, attribute=boost_attribute,
                                     value=boost_value)
            player_boosts.append(this_boost)

    player = Player(name=player_name, position=player_position, display_name=player_display_name,
                    program=player_program, team=player_team, ovr=player_ovr, adjusted_ovr=player_adjusted_ovr, 
                    type=player_type, boosts=player_boosts, auctionable=player_auctionable,
                    gp_attributes=gp_attributes, misc_attributes=misc_attributes)

    players.append(player)

  return players
