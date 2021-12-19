import logging
logger = logging.getLogger(__name__)

DEFAULT_COST_PER_UNIT = 6
DEFAULT_RAMP_UP_COST = 3

class ProfitCalculations():
    def __init(self,run_parameters):
        self._time_horizon = run_parameters['time_horizon']

    def reset(self, context,state):
        return None 
        # Not sure if I need anything in here/what I need in here.
    
    def compute_reward(self, state,action):
        reward = 0
        if action['type'] == 'advance_time':
            # assuming all bids are just accepted, can include 
            # logic around that if needed

            # calculate profit from guaranteed bids
            for quantity, price in state['firm_guaranteed']:
                reward += quantity * (price - DEFAULT_COST_PER_UNIT)
            
            # calculate revenue from backup bids
            for quantity, price in state['firm_backup']:
                reward += quantity * price

            # calculate costs for backup power
            total_guaranteed = sum(quantity for quantity, price in state['total_guaranteed'])
            backup_required = state['demand'] - total_guaranteed
            backup_promised = sum(quantity for quantity, price in state['firm_backup'])
            if backup_required > 0:
                reward -= DEFAULT_RAMP_UP_COST
                reward -= DEFAULT_COST_PER_UNIT * min(backup_promised, backup_required)
        state['firm_guaranteed'] = []
        state['firm_backup'] = []
        state['total_guaranteed'] = []
        state['total_backup'] = []
        
        return {'total':reward,
                'by_asin':None}