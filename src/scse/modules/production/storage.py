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
            self.capacity = 0

    def get_name(self):
        return 'storage_firm'

    def reset(self, context, state):
        state['storage_occupation'] = 0

    def compute_actions(self, state):
        state['storage_occupation'] = max(0,state['storage_occupation'])

        logger.debug("storage_occupation: " + str(state['storage_occupation']) + "/" + str(self.capacity))
        actions = [{
            'type': 'bid',
            'price': 80,
            'quantity': state['storage_occupation'],
            'schedule': state['clock'],
            'bidder': 'storage',
            'sd': 0,
        },{   
            'type': 'market_demand_at_price',
            'quantity': max(self.capacity - state['storage_occupation'],0),
            'price' : 60,
            'schedule': state['clock'],
            'sd' : 0,
        }]

        '''logger.debug("Buy {} at {}, sell {} at {}".
            format(actions[1]['quantity'], actions[1]['price'], 
            actions[0]['quantity'], actions[0]['price']))'''
        return actions
