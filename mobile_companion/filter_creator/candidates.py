from ..core import AuctionFilter
import itertools
from collections import namedtuple

def find_minimum_spanning_filter(targets, name_filter=None, verbose=False):
    """
    Find the smallest possible filter that matches all targets (with an optional name filter)

    """
    # TODO: should the name filter be an option here or somewhere higher?

    #
    # start by applying name filter if given
    #
    if name_filter is not None:
        f = AuctionFilter(name=name_filter)
        targets = f.filter(targets)
    else:
        f = AuctionFilter()

    #
    # and now everything else
    #
    target_min_ovr = min(player.ovr for player in targets)
    target_max_ovr = max(player.ovr for player in targets)
    target_positions = sorted(list(set(player.position for player in targets)))
    target_teams = sorted(list(set(player.team for player in targets)))
    target_types = sorted(list(set(player.type for player in targets)))

    f = AuctionFilter(name=name_filter,
               min_ovr=target_min_ovr, max_ovr=target_max_ovr,
               positions=target_positions, teams=target_teams,
               types=target_types)

    return f


def find_candidate_name_filters(targets, seqlen=2, num_candidates=5):
    '''
    Find top *num_candidates* name filters based on how many targets they match
    '''
    bad_chars = ['.', '-']
    target_names = [ player.name for player in targets ]

    all_seqs = _find_all_substrings(target_names, seqlen=seqlen)
    candidates = list(set(all_seqs))

    Result = namedtuple("Result", ["filter", "count"])
    results = []
    for icandidate, candidate in enumerate(candidates):

        # drop anything with weird characters (since we can't
        # filter these in the game anyway)

        # there's probably a more efficient way to do this check:
        if any(bad_char in candidate for bad_char in bad_chars):
            #print("Skipping: {}".format(candidate))
            continue

        f = AuctionFilter(name=candidate)
        res = Result(filter=candidate, count=len(f.filter(targets)))
        results.append(res)

    results = sorted(results, key=lambda x: x.count)

    if num_candidates is not None:
        results = results[-num_candidates:]

    return results


def _find_all_substrings(names, seqlen=2):
    '''
    Find all substrings of len *seqlen* in player names

    '''

    if seqlen == 0:
        return ['']

    seqs = []

    for name in names:
        parts = name.split()

        for part in parts:
            for i in range(len(part) - seqlen + 1):
                seq = part[i:i + seqlen]
                seqs.append(seq)

    return seqs



