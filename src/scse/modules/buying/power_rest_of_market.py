from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging

logger = logging.getLogger(__name__)
DEFAULT_GUARANTEED_PRICE = 10
DEFAULT_BACKUP_PRICE = 5
DEFAULT_MEAN = 25
DEFAULT_VAR = 2
class SimpleRestOfMarket(Agent):
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        
    def get_name(self):
        return 'market_selling_contracts'

    def reset(self, context, state):
        return None
        #self._asin_list = context['asin_list']
        # again, not sure

    def compute_actions(self, state):
        # compute the "guaranteed supply"-- whatever other firms bid
        # as guaranteed power + whatever renewables come in

        # note that at some point, state can hold information about
        # projected demand/supply that everyone has access to. Then,
        # the question is how strategies change under increasing uncertainty (renewable)
        quantity = self._rng.normal(DEFAULT_MEAN,DEFAULT_VAR)
        current_clock = state['clock']

        action = {
            'type': 'bid',
            'bid_type': 'guaranteed',
            'price': DEFAULT_GUARANTEED_PRICE,
            'quantity': quantity,
            'schedule':current_clock,
            'bidder': 0 # 0 is market
        }
        return [action]