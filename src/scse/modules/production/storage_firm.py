from scse.api.module import Agent
import logging

logger = logging.getLogger(__name__)


class StorageFirm(Agent):
    """
    Buys cheap energy and sells at a markup. 
    """

    def __init__(self, run_parameters):
        if 'storage_firm_capacity' in run_parameters:
            self.capacity = run_parameters['storage_firm_capacity']
        else:
            self.capacity = 1000000
        self.occupation = 0

    def get_name(self):
        return 'storage_firm'

    def reset(self, context, state):
        None

    def compute_actions(self, state):
        actions = [{
            'type': 'bid',
            'price': 80,
            'quantity': self.occupation,
            'schedule': state['clock'],
            'bidder': 'storage',
        },{   
            'type': 'market_demand_at_price',
            'quantity': self.capacity - self.occupation, 
            'price' : 60,
            'schedule': state['clock'],
        }]

        return actions
