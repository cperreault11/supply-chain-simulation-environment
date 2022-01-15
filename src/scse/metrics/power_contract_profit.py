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
            total_demand = state['true_demand'] + 2 * state['demand_sd']#  + state['backup_required']
            total_demand += sum(2 * bid['sd'] for bid in state['bids'])
            logger.debug("variance from renewables: {}".format(sum(2 * bid['sd'] for bid in state['bids'])))
            remaining_demand = total_demand
            all_options = sorted([(bid['bidder'], bid['price'], bid['quantity']) for bid in state['bids']], key = lambda x: x[1]) # if calculating profit for each firm, can add cost per unit here as well
            bought = []
            for bid in all_options:
                #logger.debug("demand remaining: {}".format(remaining_demand))

                quantity = min(remaining_demand, bid[2])#  .copy()[0]
                #print (remaining_demand, quantity)
                logger.debug(quantity)
                remaining_demand -= quantity
                logger.debug("quantity: {}, remaining demand: {}".format(quantity, remaining_demand))
                bought.append((bid[0], bid[1], quantity))
                if remaining_demand == 0:
                    break

            total_cost = sum(x[1] * x[2] for x in bought)
            logger.debug("Demand unfulfilled: {}".format(remaining_demand))
            logger.debug("Average cost: {}".format(total_cost/state['true_demand']))
            logger.debug(bought)
            # total cost, market demand + 2 sd, 2 sd for renewable prod, renwable prod
            print (','.join([str(total_cost), str(state['true_demand']),str(state['demand_sd']), str(sum(2 * bid['sd'] for bid in state['bids'])), str(sum(bid['quantity'] for bid in state['bids'] if bid['bidder'] == 'renewable'))]))
            # easy to calculate profit per producer as well if needed
            state['bids'] = []
            return {
                'total': total_cost,
                'by_asin': None
            }