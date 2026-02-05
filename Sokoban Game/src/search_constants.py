
# Constants to denote the search strategy.
_DEPTH_FIRST = 0
_BREADTH_FIRST = 1
_BEST_FIRST = 2
_ASTAR = 3
_UCS = 4
_CUSTOM = 5

_DEPTH_FIRST_STR = 'depth_first'
_BREADTH_FIRST_STR = 'breadth_first'
_BEST_FIRST_STR = 'best_first'
_ASTAR_STR = 'astar'
_UCS_STR = 'ucs'
_CUSTOM_STR = 'custom'

_SEARCH_STRATEGY_MAP = {
    _DEPTH_FIRST_STR : _DEPTH_FIRST,
    _BREADTH_FIRST_STR : _BREADTH_FIRST,
    _BEST_FIRST_STR : _BEST_FIRST,
    _ASTAR_STR : _ASTAR,
    _UCS_STR : _UCS,
    _CUSTOM_STR : _CUSTOM
}

# For best first and astar we use a priority queue. This requires
# a comparison function for nodes. These constants indicate if we use
# the gval, the hval or the sum of gval and hval in the comparison.
_SUM_HG = 0
_H = 1
_G = 2
_C = 3

# Cycle Checking. Either CC_NONE 'none' (no cycle checking), CC_PATH
# 'path' (path checking only) or CC_FULL 'full' (full cycle checking,
# remembering all previously visited nodes).
_CC_NONE = 0
_CC_PATH = 1
_CC_FULL = 2

_CC_NONE_STR = 'none'
_CC_PATH_STR = 'path'
_CC_FULL_STR = 'full'
_CC_DEFAULT_STR = 'default'

_CYCLE_CHECK_MAP = {
    _CC_DEFAULT_STR : _CC_FULL,
    _CC_NONE_STR : _CC_NONE,
    _CC_PATH_STR : _CC_PATH,
    _CC_FULL_STR : _CC_FULL
}
