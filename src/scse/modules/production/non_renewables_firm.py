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

    DEFAULT_RAMP_UP_COST = 40
    DEFAULT_COST_PER_UNIT = 3

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

    def get_name(self):
        return 'static_firm'

    def reset(self, context, state):
        return None

    def compute_actions(self, state):
        current_clock = state['clock']
        capacity = self.supply_model.predict(state['date_time'])
        action = {
            'type': 'bid',
            'price': self.default_price,
            'quantity': capacity,
            'schedule': current_clock,
            'bidder': 'static',
            # 'cost_pu': self.DEFAULT_COST_PER_UNIT,
            # 'ramup_cost': self.DEFAULT_RAMP_UP_COST,
        }
        #logger.debug("static firm produced {} units of power".format(capacity))
        actions = [action]
        return actions
