from scse.api.module import Agent
import numpy as np
import scipy.stats
import logging

logger = logging.getLogger(__name__)
DEFAULT_GUARANTEED_PRICE = 10
DEFAULT_BACKUP_PRICE = 5
DEFAULT_CAPACITY = 10
class SimpleFlexibleFirm(Agent):
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.capacity = DEFAULT_CAPACITY
        
    def get_name(self):
        return 'selling_contracts'
    
    def reset(self, context, state):
        return None
        # again, not sure what belongs in here
    
    def compute_actions(self, state):
        guaranteed_power = .5 # ratios
        backup_power = .5
        not_sold = 0
        current_clock = state['clock']
        # might need to do one asin for each type of purchase, although
        # that gets a little bit weird. Look further into the 
        # 'settling' functions and see what othe types of 
        # things I can add into the state.

        # For now: fixed price. remaining supply is just a random 
        # draw based on renewables, what's available, etc.
        # that should be easy enough to test and modify in the future

        # If I can get that working, set up a meeting with the others
        # and discuss what type of experiments we actually want to setup
        # and it should be easy to make the code modifications at that
        # point 

        # In this simplest model, it's assumed that someone else can cover
        # up the backup supply as needed. It's not really important, it's 
        # just how to get something up and running quickly

        # the structure of these actions will depend on how I can make the 
        # profit calculations, so I'll need to look at that.
        action1 = {
            'type': 'bid',
            'bid_type': 'guaranteed',
            'price': DEFAULT_GUARANTEED_PRICE,
            'quantity': guaranteed_power * self.capacity,
            'schedule': current_clock,
            'bidder': 1 # 1 is bidder of interest
        }
        action2 = {
            'type': 'bid',
            'bid_type': 'backup',
            'price': DEFAULT_BACKUP_PRICE,
            'quantity': backup_power * self.capacity,
            'schedule': current_clock,
            'bidder': 1
        }
        actions = [action1, action2]
        return actions