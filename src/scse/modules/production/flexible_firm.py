from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging


logger = logging.getLogger(__name__)

class FlexibleFirm(Agent):
    """
    Flexible firm, like a natural gas company
    """
    DEFAULT_RAMP_UP_COST = 20
    DEFAULT_COST_PER_UNIT = 6
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = run_parameters['flexible_capacity']
        self.default_price = run_parameters['flexible_price']
        
    def get_name(self):
        return 'flexible_firm'
    
    def reset(self, context, state):
        return None
        # again, not sure what belongs in here
    
    def compute_actions(self, state):
        current_clock = state['clock']
        # if we want to incorporate strategy to these bids, 'quantity' can 
        # be set to the maximum that the firm is willing to sell at either
        # guaranteed or backup power, set the other price to inf
        action = {
            'type': 'bid',
            'price': self.default_price,
            'quantity': self.capacity,
            'schedule': current_clock,
            'bidder': 'flexible',
            'rampup_cost': self.DEFAULT_RAMP_UP_COST,
            'cost_pu': self.DEFAULT_COST_PER_UNIT
        }
        actions = [action]
        return actions