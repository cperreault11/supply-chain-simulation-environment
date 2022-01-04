import numpy as np
from scse.api.module import Agent
import scipy.stats

import logging
logger = logging.getLogger(__name__)
VAR = 5 # could set these with run params if we want
class NormalPowerDemand(Agent):


    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.mean = run_parameters['mean_demand']
        self.var = VAR
    
    def get_name(self):
        return 'demand_generator'

    def reset(self,context,state):
        return None

    def compute_actions(self, state):
        actions = []
        x = self._rng.rand()
        # truncated normal, can't have negative demand
        demand =  self.mean + scipy.stats.norm.ppf(1 - x * (1 - scipy.stats.norm.cdf(-self.mean/self.var))) # TODO: switch to truncnorm
        action = { # most of these are unnecessary fillers leftover from newsvendor demo
            'type': 'market_demand',
            'asin': 1,
            'origin': None,
            'destination': None,
            'quantity': demand,
            'schedule': state['clock']
        }
        logger.debug("Market bought {} units of power".format(demand))
        actions.append(action)
        
        return actions
