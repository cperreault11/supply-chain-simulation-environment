from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging
from scse.modules.production.supply_model import SupplyModel

logger = logging.getLogger(__name__)


class RenewablesFirm(Agent):
    """
    Produces energy from renewables sources, such as wind or solar.
    Less predictable output, higher price per MW.
    """
    # DEFAULT_RAMP_UP_COST = 20
    # DEFAULT_COST_PER_UNIT = 6

    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
      #self.capacity = run_parameters['variable_capacity']
        self.default_price = run_parameters['variable_price']
        self.supply_model = SupplyModel(
            model_name='supply-model-ren',
            mean=0.400,
            var=0.050,
            offset=run_parameters['renewable_offset'],
            scale=run_parameters['renewable_scale']
            )
        self.bid_amount = 3
        self.bid_percent_increase = 0.1

    def get_name(self):
        return 'renewables_firm'

    def reset(self, context, state):
        return None
        # again, not sure what belongs in here

    def get_bid_price(self, bid_number):
        bid_factor = self.bid_percent_increase * \
            ((bid_number - self.bid_amount//2) +
             (bid_number >= self.bid_amount//2 and not self.bid_amount % 2))
        return self.default_price * (1 + bid_factor)

    def compute_actions(self, state):
        current_clock = state['clock']
        capacity,sd = self.supply_model.predict(state['date_time'])
        # if we want to incorporate strategy to these bids, 'quantity' can
        # be set to the maximum that the firm is willing to sell at either
        # guaranteed or backup power, set the other price to inf
        actions = [{
            'type': 'bid',
            'price': self.get_bid_price(bid_number),
            'quantity': capacity / self.bid_amount,
            'schedule': current_clock,
            'bidder': 'renewable',
            'sd':sd
            # 'rampup_cost': self.DEFAULT_RAMP_UP_COST,
            # 'cost_pu': self.DEFAULT_COST_PER_UNIT
        } for bid_number in range(self.bid_amount)]
        logger.debug(f'{self.get_name()} produced {capacity} MW, sd {sd}')
        #prices = [bid['price'] for bid in actions]
        #logger.debug(f'Bid prices: {prices}')
        return actions
