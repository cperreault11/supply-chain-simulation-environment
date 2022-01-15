from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging
logger = logging.getLogger(__name__)
class CheapRampFirm(Agent):
    """
    Flexible firm, like a natural gas company
    """
    DEFAULT_PRICE_POINTS = [0.95, 1, 1.05]
    DEFAULT_QUANITITES = [0.7, 0.2, .1]
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = run_parameters['flexible_capacity']
        self.default_price = run_parameters['flexible_price']

    def get_name(self):
        return 'cheap_ramp_firm'

    def compute_actions(self, state):
        # guaranteed or backup power, set the other price to inf
        current_clock = state['clock']
        actions = []
        for i,pp in enumerate(self.DEFAULT_PRICE_POINTS):
            actions.append({
            'type': 'bid',
            'price': self.default_price * pp,
            'quantity': self.capacity * self.DEFAULT_QUANITITES[i],
            'schedule': current_clock,
            'bidder': 'cheap_ramp',
            'sd':0
            })
        #logger.debug("flexible firm offers {} units of standard power and {} units of backup power".format(guaranteed_power* self.capacity, backup_power* self.capacity))
        return actions 