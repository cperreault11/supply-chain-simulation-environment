from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging

from scse.modules.buying.power_rest_of_market import DEFAULT_BACKUP_PRICE

logger = logging.getLogger(__name__)

class StaticFirm(Agent):
    """
    Static firm, like coal. High ramp up costs, cannot adjust
    production quantities well
    """

    DEFAULT_RAMP_UP_COST = 40
    DEFAULT_COST_PER_UNIT = 3
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = run_parameters['static_capacity']
        self.guaranteed_price = run_parameters['spg']
        self.backup_price = run_parameters['spb']

    def get_name(self):
        return 'static_firm'

    def reset(self, context, state):
        return None

    def compute_actions(self, state):
        current_clock = state['clock']
        action = {
            'type': 'bid',
            'price_guaranteed': self.guaranteed_price,
            'price_backup': self.backup_price,
            'quantity': self.capacity,
            'schedule': current_clock,
            'bidder': 'static',
            'cost_pu': self.DEFAULT_COST_PER_UNIT,
            'ramup_cost': self.DEFAULT_RAMP_UP_COST,
        }
        #logger.debug("static firm produced {} units of power".format(produce * self.capacity))
        actions = [action]
        return actions