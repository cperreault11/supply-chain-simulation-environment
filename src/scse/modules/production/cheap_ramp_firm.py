from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging
logger = logging.getLogger(__name__)
class CheapRampFirm(Agent):
    """
    Flexible firm, like a natural gas company
    """

    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = run_parameters['flexible_capacity']
        self.default_price = run_parameters['flexible_price']
        self.bid_amount = 3
        self.bid_percent_increase = 0.05

    def get_name(self):
        return 'cheap_ramp_firm'

    def get_bid_price(self, bid_number):
        bid_factor = self.bid_percent_increase * \
            ((bid_number - self.bid_amount//2) +
             (bid_number >= self.bid_amount//2 and not self.bid_amount % 2))
        return self.default_price * (1 + bid_factor)

    def compute_actions(self, state):
        # guaranteed or backup power, set the other price to inf
        current_clock = state['clock']
        actions = [{
            'type': 'bid',
            'price': self.get_bid_price(bid_number),
            'quantity': self.capacity / self.bid_amount,
            'schedule': current_clock,
            'bidder': 'cheap_ramp',
            'sd':0
            } for bid_number in range(self.bid_amount)]
        #logger.debug("flexible firm offers {} units of standard power and {} units of backup power".format(guaranteed_power* self.capacity, backup_power* self.capacity))
        return actions 