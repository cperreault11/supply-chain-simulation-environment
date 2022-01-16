import logging
import scipy.optimize
import numpy as np
logger = logging.getLogger(__name__)

class ProfitCalculations():
    def __init__(self,run_parameters):
        self._time_horizon = run_parameters['time_horizon']

    def reset(self,context,state):
        state['bids'] = []

    def compute_reward(self, state, action):
        if action['type'] == 'advance_time':
            total_demand = state['predicted_demand'] + state['backup_required']
            remaining_demand = total_demand
            all_options = sorted([(bid['bidder'], bid['price'], bid['quantity']) for bid in state['bids']], key = lambda x: x[1]) # if calculating profit for each firm, can add cost per unit here as well
            bought = []

            for bid in all_options:
                quantity = max(0,min(remaining_demand, bid[2]))
                remaining_demand -= quantity
                bought.append((bid[0], bid[1], quantity))
                if remaining_demand == 0:
                    break

            # demand with price limit calculation 
            remaining_demand = state['demand_at_price']['quantity']
            price_limit = state['demand_at_price']['price']
            
            for bid in all_options:
                if remaining_demand == 0 or price_limit > bid[1]:
                    break

                quantity = max(0,min(remaining_demand, bid[2]))
                remaining_demand -= quantity
                bought.append((bid[0], bid[1], quantity))

            total_cost = sum(x[1] * x[2] for x in bought)
            logger.debug("Demand unfulfilled: {}".format(remaining_demand))
            logger.debug("Average cost: {}".format(total_cost/state['true_demand']))
            # easy to calculate profit per producer as well if needed
            state['bids'] = []

            return {
                'total': total_cost,
                'by_asin': None
            }