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
    DEFAULT_RAMP_UP_COST = 20
    DEFAULT_COST_PER_UNIT = 6

    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = run_parameters['variable_capacity']
        self.default_price = run_parameters['variable_price']
        self.supply_model = SupplyModel(
            model_name='supply-model-ren',
            mean=0.400,
            var=0.050,
            offset=self.capacity/2,
            scale=self.capacity
        )

    def get_name(self):
        return 'renewables_firm'

    def reset(self, context, state):
        return None
        # again, not sure what belongs in here

    def compute_actions(self, state):
        current_clock = state['clock']
        capacity,var = self.supply_model.predict(state['date_time'])
        # if we want to incorporate strategy to these bids, 'quantity' can
        # be set to the maximum that the firm is willing to sell at either
        # guaranteed or backup power, set the other price to inf
        action = {
            'type': 'bid',
            'price': self.default_price,
            'quantity': capacity[0][0],
            'schedule': current_clock,
            'bidder': 'renewable',
            'sd': np.sqrt(var)[0]
        }
        logger.debug("Renewable firm produced {} units of power with sd {}".format(capacity, np.sqrt(var)))
        actions = [action]
        return actions
