import numpy as np
from scse.api.module import Agent
import scipy.stats

import logging
logger = logging.getLogger(__name__)

class NormalPowerDemand(Agent):
    MEAN = 30
    VAR = 5 # could set these with run params if we want

    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        # not sure if I need anything else here?
    
    def get_name(self):
        return 'demand_generator'

    def reset(self,context,state):
        return None
        # this may be unnecessary
        #self._asin_list = context['asin_list']

    def compute_actions(self, state):
        actions = []
        x = self._rng.rand()
        # truncated normal, can't have negative demand
        demand =  self.MEAN + scipy.stats.norm.ppf(1 - x * (1 - scipy.stats.norm.cdf(-self.MEAN/self.VAR)))
        action = {
            'type': 'market_demand',
            # everything is tracked by asin, we only have a single 'product'
            'asin': 1,
            'origin': None,
            'destination': None, # Not sure what this needs to be
            'quantity': demand,
            'schedule': state['clock']
        }
        logger.debug("Market bought {} units of power".format(demand))
        actions.append(action)
        
        return actions
