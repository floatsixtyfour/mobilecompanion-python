import mobile_companion.database as MDB
import mobile_companion.team as MT
import mobile_companion.calculators as MCC
import mobile_companion.team_optimizer.meta as META
import copy, pickle
from datetime import timedelta

outfile = 'best_overall.dat'
res = dict()
calc = MCC.Standard('../standard_weights.dat')

obj_func = lambda x: calc.calculate(x)[1]['overall']['rounded']

player_db = MDB.import_database_csv('../player_database.csv')
dates = sorted(set([p.date_added for p in player_db]))

start_date = dates[0]
end_date = dates[-1]

print("Running analysis on dates {} to {}".format(start_date, end_date))

current_date = start_date
prior_best_team = None

while current_date <= end_date:
    current_players = [ p for p in player_db if p.date_added <= current_date ]
    print("Starting {} [ {} players ]".format(current_date, len(current_players)))

    best_team, best_obj = META.optimize(current_players, obj_func, initial_guess=prior_best_team)

    res[current_date] = (best_team, best_obj)
    pickle.dump(res, open(outfile, 'wb'))

    current_date = current_date + timedelta(days=7)
    prior_best_team = best_team
    print("Best obj: {}".format(best_obj))
    print("")

