import logging
import scipy.optimize
import numpy as np
logger = logging.getLogger(__name__)

class ProfitCalculations():
    def __init__(self,run_parameters):
        self._time_horizon = run_parameters['time_horizon']

    def reset(self,context,state):
        state['bids'] = []
        # state['total_guaranteed'] = []
        # state['total_backup'] = []
    
    def compute_reward(self, state,action):
        #### TODO: summarize the pricing decisions here
        #### note that these are initial choices, market structure can change if that is useful.
        reward = 0
        if action['type'] == 'advance_time':
            true_demand = state['true_demand']
            predicted_demand = state['predicted_demand']
            backup_demand = state['backup_required']
            # init potential metrics
            profit_by_producer = {}
            cost = 0
            # init lin programming variables
            cons_mins = []
            cons_maxs = []
            cons_coeff = []
            initial = []
            bounds = []
            predicted_remaining = predicted_demand
            backup_remaining = backup_demand
            for i,bid in enumerate(state['bids']):
                quantity_guaranteed = min(bid['quantity'], predicted_remaining)
                predicted_remaining -= quantity_guaranteed
                initial.extend([bid['price_guaranteed'], quantity_guaranteed])
                bounds.append((bid['price_guaranteed'],bid['price_guaranteed']))
                bounds.append((0,bid['quantity']))
                quantity_backup = max(0, min(bid['quantity'] - quantity_guaranteed, backup_remaining))
                backup_remaining -= quantity_backup
                initial.extend([bid['price_backup'],quantity_backup])
                bounds.append((bid['price_backup'],bid['price_backup']))
                bounds.append((0,bid['quantity']))
                cons_mins.append(bid['price_guaranteed'])
                cons_maxs.append(bid['price_guaranteed'])
                cons_mins.append(bid['price_backup'])
                cons_maxs.append(bid['price_backup'])
                cons_mins.append(0)
                cons_maxs.append(bid['quantity'])
                cons_mins.append(0)
                cons_maxs.append(bid['quantity'])
                cons_mins.append(0)
                cons_maxs.append(bid['quantity'])
                c1 = np.zeros(4 * len(state['bids']))
                c1[4 * i] = 1
                c2 = np.zeros(4 * len(state['bids']))
                c2[4 * i + 2] = 1
                c3 = np.zeros(4 * len(state['bids']))
                c3[4 * i + 1] = 1
                c3[4 * i + 3] = 1
                c4 = np.zeros(4 * len(state['bids']))
                c4[4 * i + 1] = 1
                c5 = np.zeros(4 * len(state['bids']))
                c5[4 * i + 3] = 1
                cons_coeff.extend([c1,c2,c3,c4,c5])
            cons_mins.append(predicted_demand)
            cons_maxs.append(predicted_demand)
            cons_mins.append(backup_demand)
            cons_maxs.append(backup_demand)
            c1 = np.zeros(4 * len(state['bids']))
            c2 = np.zeros(4 * len(state['bids']))
            for i in range(len(state['bids'])):
                c1[4 * i + 1] = 1
                c2[4 * i + 3] = 1
            cons_coeff.extend([c1,c2])
            constraints = scipy.optimize.LinearConstraint(np.array(cons_coeff), np.array(cons_mins), np.array(cons_maxs))
            t = scipy.optimize.minimize(self.equivalent_cost, initial, constraints=constraints, options={'maxiter': 100},method ="trust-constr") # check for success?
            res = t.x
            res[res < 1e-4] = 0
            cost = self.total_cost(res)
            logger.debug(res)
            state['bids'] = []
            return {'total':cost,
                'by_asin':None}

    def total_cost(self,bought):
        """Objective function to be minimized when determining purchases to make"""
        max_guaranteed = max((x for i,x in enumerate(bought) if i % 4 == 0 and bought[i+1] > 0),default=0)
        max_backup = max((x for i,x in enumerate(bought) if i % 4 == 2 and bought[i+1] > 0),default=0)
        return sum(x * max_guaranteed for i,x in enumerate(bought) if i % 4 == 1) + sum(x * max_backup for i,x in enumerate(bought) if i % 4 == 3)

    def equivalent_cost(self, bought):
        """will have an equivalent minimum with better gradients for optimization"""
        return sum(bought[i] * bought[i+1] for i,x in enumerate(bought) if i % 2 == 0 and x!=np.inf and x!=np.nan)