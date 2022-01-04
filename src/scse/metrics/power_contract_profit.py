import logging
logger = logging.getLogger(__name__)

class ProfitCalculations():
    def __init__(self,run_parameters):
        self._time_horizon = run_parameters['time_horizon']

    def reset(self,context,state):
        state['guaranteed'] = []
        state['backup'] = []
        # state['total_guaranteed'] = []
        # state['total_backup'] = []
    
    def compute_reward(self, state,action):
        reward = 0
        if action['type'] == 'advance_time':
            # assuming all bids are just accepted, can include 
            # logic around that if needed

            # calculate profit from guaranteed bids
        #     guar_reward = 0
        #     for quantity, price in state['firm_guaranteed']:
        #         guar_reward += quantity * (price - DEFAULT_COST_PER_UNIT)
        #     reward += guar_reward
        #     logger.debug("Profit from guaranteed power {}".format(guar_reward))
        #     # calculate revenue from backup bids
        #     rev = 0
        #     for quantity, price in state['firm_backup']:
        #         rev += quantity * price
        #     reward+= rev
        #     logger.debug("Revenue from backup power {}".format(rev))

        #     # calculate costs for backup power
        #     total_guaranteed = sum(quantity for quantity, price in state['total_guaranteed'])
        #     backup_required = state['demand'] - total_guaranteed
        #     backup_promised = sum(quantity for quantity, price in state['firm_backup'])
        #     logger.debug("Backup power used: {}".format(min(backup_promised,backup_required)))
        #     if backup_required > 0:
        #         reward -= DEFAULT_RAMP_UP_COST
        #         reward -= DEFAULT_COST_PER_UNIT * min(backup_promised, backup_required)
        # state['firm_guaranteed'] = []
        # state['firm_backup'] = []
        # state['total_guaranteed'] = []
        # state['total_backup'] = []
        
        



            # first calculate which bids are accepted
            demand = state['demand']
            remaining_demand = demand
            standard_bought = [] # dict of producer id, profit
            backup_bought = []
            # preprocess the actions to get a set of potential purchases
            guaranteed_options = sorted(state['guaranteed'].copy(), key = lambda x: x[1])
            for offer in guaranteed_options:
                quantity = max(0,min(remaining_demand, offer[0]))
                remaining_demand -= quantity
                standard_bought.append((quantity, offer[1], offer[2], offer[3])) # quantity, price, cost, producer
                if remaining_demand == 0:
                    break
            backup_options = sorted(state['backup'].copy(), key=lambda x: x[1])
            if remaining_demand > 0:
                # backup required = remaining demand
                # just need to figure out the difference between profit and consumer cost when we hit backup power
                for offer in backup_options:
                    quantity = max(0,min(remaining_demand, offer[0]))
                    remaining_demand -= quantity
                    backup_bought.append((quantity, offer[1], offer[2], offer[3], offer[4], offer[5])) # quantity, price, cost, producer, rampup cost, price if used
                    if remaining_demand == 0:
                        break
            logger.debug("remaining demand: {}".format(remaining_demand))
            logger.debug("standard power bought: {}".format(sum(x[0] for x in standard_bought)))
            profit_by_producer = {}
            avg_cost = 0
            for producer in ['flexible', 'static','variable']:
                profit_by_producer[producer] = sum(x[0]* (x[1] - x[2]) for x in standard_bought if x[3] == producer)
            # backup profit
            # assuming that all backup power offered is bought for now, it might make sense to buy enough backup power for 
            # 99% chance of no outage
            backup_used_total = sum(x[0] for x in backup_bought)
            logger.debug("backup power used: {} ".format(backup_used_total))
            if backup_used_total > 0 and len(backup_options) > 0: # for now, there is only one firm that can produce backup options, so no looping
                # sum this way
                profit_by_producer['flexible'] += backup_used_total * (backup_options[0][5] - backup_options[0][2]) - backup_options[0][4] + (backup_options[0][0] - backup_used_total) * backup_options[0][1]
            else:
                profit_by_producer['flexible'] += backup_options[0][0] * backup_options[0][1]

            avg_cost = (sum(x[0] * x[1] for x in standard_bought) + backup_options[0][1] * (backup_options[0][0] - backup_used_total)* backup_options[0][1] + backup_used_total * backup_options[0][5]) /demand
            state['guaranteed'] = []
            state['backup'] = []
            return {'total':profit_by_producer['flexible'],
                'by_asin':None}