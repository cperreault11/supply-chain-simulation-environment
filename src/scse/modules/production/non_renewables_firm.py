from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging
from scse.modules.production.supply_model import SupplyModel
from scse.modules.buying.power_rest_of_market import DEFAULT_BACKUP_PRICE

logger = logging.getLogger(__name__)


class NonRenewablesFirm(Agent):
    """
    Produces power from a non-renewables source, such as coal or natural gas.
    More predictable output, higher cost per MW.
    """

    # DEFAULT_RAMP_UP_COST = 40
    # DEFAULT_COST_PER_UNIT = 3

    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = run_parameters['static_capacity']
        self.default_price = run_parameters['static_price']
        self.supply_model = SupplyModel(
            model_name='supply-model-non-ren',
            mean=0.418,
            var=0.056,
            offset=1557416.5,
            scale=1357952.1
        )
        self.bid_amount = 3
        self.bid_percent_increase = 0.1

    def get_name(self):
        return 'non_renewables_firm'

    def reset(self, context, state):
        return None

    def get_bid_price(self, bid_number):
        bid_factor = self.bid_percent_increase * \
            ((bid_number - self.bid_amount//2) +
             (bid_number >= self.bid_amount//2 and not self.bid_amount % 2))
        return self.default_price * (1 + bid_factor)

    def compute_actions(self, state):
        current_clock = state['clock']
        capacity = self.supply_model.predict(state['date_time'])
        actions = [{
            'type': 'bid',
            'price': self.get_bid_price(bid_number),
            'quantity': capacity / self.bid_amount,
            'schedule': current_clock,
            'bidder': 'flexible',
            # 'rampup_cost': self.DEFAULT_RAMP_UP_COST,
            # 'cost_pu': self.DEFAULT_COST_PER_UNIT
        } for bid_number in range(self.bid_amount)]
        logger.debug(f'{self.get_name()} produced {capacity} MW')
        prices = [bid['price'] for bid in actions]
        logger.debug(f'Bid prices: {prices}')
        return actions
