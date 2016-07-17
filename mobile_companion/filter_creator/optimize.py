from __future__ import division, print_function

from . import candidates as mfc
import copy
from collections import namedtuple, Counter

FilterResult = namedtuple("Result", ['filter', 'num_matched_targets', 'num_matched_universe', 'ratio'])

def find_filters(targets, universe, min_name_len=1, max_name_len=5, num_filters=10,
                 obj_func=lambda x: x.ratio, verbose=False):
    """
    Find "optimal" filters with name filters of various lenghts

    """

    results = []
    for name_len in range(min_name_len, max_name_len + 1):
        candidate_name_filters = mfc.find_candidate_name_filters(targets,
                                                                 seqlen=name_len,
                                                                 num_candidates=10)

        for icandidate, candidate in enumerate(candidate_name_filters):
            name_filter = candidate.filter

            if verbose:
                print("Starting filter: {}".format(name_filter))

            # only use filtered universe from now on as this will reduce total
            # number of names to search through (and since filtered universe is widest
            # possilbe universe to match from here on anyway)
            f = mfc.find_minimum_spanning_filter(targets, name_filter=name_filter)
            filtered_universe = f.filter(universe)

            #res = iterate_one_step(f, targets, filtered_universe)
            res = optimize_filter(f, targets, filtered_universe, obj_func=obj_func)
            results.append(res)

    results = sorted(results, key=lambda (res, obj): obj)

    if num_filters is not None:
        results = results[-num_filters:]

    return results


def optimize_filter(filter, targets, universe, obj_func=lambda x: x.ratio, verbose=False):
    """
    Try to improve filter by tightening its constraints

    """

    matched_universe = filter.filter(universe)
    matched_targets = filter.filter(targets)
    num_matched_targets = len(matched_targets)
    num_matched_universe = len(matched_universe)
    matched_ratio = num_matched_targets / num_matched_universe

    if verbose:
      print("Current ratio: {:.1%} [{} / {}]".format(matched_ratio,
                                                     len(matched_targets), len(matched_universe)))

    res_best = FilterResult(filter=filter, num_matched_targets=num_matched_targets, num_matched_universe=num_matched_universe,
                            ratio=matched_ratio)
    obj_best = obj_func(res_best)

    res_cur = res_best
    obj_cur = obj_best - 1.0

    while obj_best > obj_cur:
        res_cur, obj_cur = _iterate_one_step(res_cur, targets, universe, obj_func)

        if obj_cur > obj_best:
            res_best = res_cur
            obj_best = obj_cur

    return res_best, obj_best


def _iterate_one_step(filter_res, targets, universe, obj_func, verbose=False):

    iter_functions = { 'max_ovr': _iterate_max_ovr_filter,
                       'min_ovr': _iterate_min_ovr_filter,
                       'position': _iterate_position_filter,
                       'team': _iterate_team_filter,
                       'type': _iterate_type_filter }

    res_best = filter_res
    obj_best = obj_func(res_best)

    res_cur = res_best

    for iter_name, iter_function in iter_functions.iteritems():
        res_new = iter_function(res_cur.filter, targets, universe)

        if res_new is None:
          continue

        step_cur, res_cur = res_new
        obj_cur = obj_func(res_cur)

        if obj_cur > obj_best:
          res_best = res_cur
          obj_best = obj_cur

    return res_best, obj_best



def _iterate_min_ovr_filter(filter, targets, universe, obj_func=lambda x: x.ratio):
    """
    Determine best new min ovr filter value

    """
    matched_targets = filter.filter(targets)
    matched_universe = filter.filter(universe)
    matched_targets_ovrs = sorted(list(set(player.ovr for player in matched_targets)))

    num_matched_targets_orig = len(matched_targets)
    num_matched_universe_orig = len(matched_universe)

    res = []
    for min_ovr_cur in matched_targets_ovrs:
        filter_cur = copy.deepcopy(filter)
        filter_cur.min_ovr = min_ovr_cur

        num_matched_targets_cur = len(filter_cur.filter(targets))
        num_matched_universe_cur = len(filter_cur.filter(universe))

        if num_matched_universe_cur > 0:
            ratio = num_matched_targets_cur / num_matched_universe_cur

            r = FilterResult(filter=filter_cur,
                             num_matched_targets=num_matched_targets_cur,
                             num_matched_universe=num_matched_universe_cur,
                             ratio=ratio)

            res.append((min_ovr_cur, r))

    if len(res) == 0:
      return None

    res = sorted(res, key=lambda (step, fres): obj_func(fres))
    best_res = res[-1]

    return best_res

def _iterate_max_ovr_filter(filter, targets, universe, obj_func=lambda x: x.ratio):
    """
    Determine best new max ovr filter value

    """
    matched_targets = filter.filter(targets)
    matched_universe = filter.filter(universe)
    matched_targets_ovrs = sorted(list(set(player.ovr for player in matched_targets)))

    num_matched_targets_orig = len(matched_targets)
    num_matched_universe_orig = len(matched_universe)

    res = []
    for max_ovr_cur in matched_targets_ovrs:
        filter_cur = copy.deepcopy(filter)
        filter_cur.max_ovr = max_ovr_cur

        num_matched_targets_cur = len(filter_cur.filter(targets))
        num_matched_universe_cur = len(filter_cur.filter(universe))

        if num_matched_universe_cur > 0:
            ratio = num_matched_targets_cur / num_matched_universe_cur

            r = FilterResult(filter=filter_cur,
                             num_matched_targets=num_matched_targets_cur,
                             num_matched_universe=num_matched_universe_cur,
                             ratio=ratio)

            res.append((max_ovr_cur, r))

    if len(res) == 0:
      return None


    res = sorted(res, key=lambda (step, fres): obj_func(fres))
    best_res = res[-1]

    return best_res


def _iterate_team_filter(filter, targets, universe, obj_func=lambda x: x.ratio):
    """
    Find best team to drop from existing filter

    """

    res = _iterate_set_filter(filter, 'teams', targets, universe, obj_func=obj_func)
    return res

def _iterate_position_filter(filter, targets, universe, obj_func=lambda x: x.ratio):
    """
    Find best position to drop from existing filter

    """

    res = _iterate_set_filter(filter, 'positions', targets, universe, obj_func=obj_func)
    return res

def _iterate_type_filter(filter, targets, universe, obj_func=lambda x: x.ratio):
    """
    Find best type to drop from existing filter

    """

    res = _iterate_set_filter(filter, 'types', targets, universe)
    return res


def _iterate_set_filter(filter, set_name, targets, universe, obj_func=lambda x: x.ratio):
    """
    Find best item to drop from given set

    """
    set_orig = copy.copy(getattr(filter, set_name))


    #
    # instead of creating running filter with each item removed one a time,
    # we'll take a shortcut and just count up the matched targets/universe by
    # item in set and use that to figure out the difference from removing each item
    #
    matched_targets_orig = filter.filter(targets)
    matched_universe_orig = filter.filter(universe)

    num_matched_targets_orig = len(matched_targets_orig)
    num_matched_universe_orig = len(matched_universe_orig)

    # now figure out how many players match each unique value in this set
    matched_targets_per_item = Counter([ getattr(p, set_name[:-1]) for p in matched_targets_orig ])
    matched_universe_per_item = Counter([ getattr(p, set_name[:-1]) for p in matched_universe_orig ])


    #
    # now figure out number of matched players if we drop each key (item) from set
    #
    res = []

    all_items = list(set(list(matched_targets_per_item.keys()) +
                         list(matched_universe_per_item.keys())))

    for item in all_items:
      # we use get(, 0) since item may not be in a member of new sets
      num_matched_targets_cur = (num_matched_targets_orig - matched_targets_per_item.get(item, 0))
      num_matched_universe_cur = (num_matched_universe_orig - matched_universe_per_item.get(item, 0))

      if num_matched_universe_cur > 0:
        ratio_cur = num_matched_targets_cur / num_matched_universe_cur

        # create new filter with item removed
        set_cur = copy.copy(set_orig)
        set_cur.remove(item)
        filter_cur = copy.copy(filter)
        setattr(filter_cur, set_name, set_cur)

        r = FilterResult(filter=filter_cur,
                         num_matched_targets=num_matched_targets_cur,
                         num_matched_universe=num_matched_universe_cur,
                         ratio=ratio_cur)

        res.append((item, r))

    if len(res) == 0:
      return None

    res = sorted(res, key=lambda (step, fres): obj_func(fres))
    best_res = res[-1]

    return best_res
