from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging

logger = logging.getLogger(__name__)

class VariableFirm(Agent):
    """
    Firm with variable power production, e.g. renewables
    """
    DEFAULT_COST_PER_UNIT = 0
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = run_parameters['variable_capacity']
        self.default_price = run_parameters['variable_price']

    def get_name(self):
        return 'variable_firm'

    def reset(self, context,state):
        return None

    def get_power_produced(self,state):
        mean = .5 * self.capacity # these should be modifiable
        var = .3 * self.capacity
        sample = self._rng.rand()
        return scipy.stats.truncnorm((0 - mean) / var, (self.capacity - mean) / var, loc=mean, scale=var).ppf(sample)


    def compute_actions(self, state):
        current_clock = state['clock']
        power_produced = int(self.get_power_produced(state))
        action = {
            'type': 'bid',
            'price': self.default_price,
            'quantity': power_produced,
            'schedule': current_clock,
            'bidder': 'variable',
            'rampup_cost': np.inf, # impossible to ramp
            'cost_pu': self.DEFAULT_COST_PER_UNIT,
        }
        logger.debug("variable firm produced {} units of power".format(power_produced))
        actions = [action]
        return actions