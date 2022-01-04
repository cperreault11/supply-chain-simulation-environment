from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging

logger = logging.getLogger(__name__)

class StaticFirm(Agent):
    """
    Static firm, like coal. High ramp up costs, cannot adjust
    production quantities well
    """
    DEFAULT_GUARANTEED_PRICE = 7
    DEFAULT_COST_PER_UNIT = 3
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = run_parameters['static_capacity']

    def get_name(self):
        return 'static_firm'

    def reset(self, context, state):
        return None

    def compute_actions(self, state):
        current_clock = state['clock']
        produce = 1 # percentage of total capacity to produce at this timestep
        action = {
            'type': 'bid',
            'bid_type': 'guaranteed',
            'price': self.DEFAULT_GUARANTEED_PRICE,
            'quantity': produce * self.capacity,
            'schedule': current_clock,
            'bidder': 'static',
            'cost_pu': self.DEFAULT_COST_PER_UNIT
        }
        actions = [action]
        return actions