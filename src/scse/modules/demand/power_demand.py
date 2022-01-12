import numpy as np
from scse.api.module import Agent
import scipy.stats
import GPy
import os
from IPython import embed

def normalize_single_feature(arr, arr_min, arr_max):
    return ((arr - arr_min)/(arr_max-arr_min))

class DemandModel():
    def __init__(self):
        path = os.path.abspath("src/scse/modules/demand/demand-model.zip")
        self.gpy_model = GPy.models.GPRegression.load_model(path)

    def predict(self, date, previous_value):
        day_of_week = normalize_single_feature(date.weekday(), 0, 6)
        month = normalize_single_feature(date.month, 0, 11)
        x = np.array([month, day_of_week, previous_value / 15000.0])
        #embed()
        X = np.array([x])
        y = self.gpy_model.predict(X)
        return y[0][0][0] * 15000

import logging
logger = logging.getLogger(__name__)
VAR = 5 # could set these with run params if we want
class NormalPowerDemand(Agent):
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.mean = run_parameters['mean_demand']
        self.var = VAR
        self.model = DemandModel()
        self.previous_demand = 5000

    def get_name(self):
        return 'demand_generator'

    def reset(self,context,state):
        return None

    def compute_actions(self, state):
        demand = self.model.predict(state['date_time'], self.previous_demand)
        self.previous_demand = demand
        
        actions = []
        x = self._rng.rand()
        # truncated normal, can't have negative demand
        mean = self.mean # this can change by time series if we switch it to that
        var = self.var # again, this can change by time series.
        #sample = self._rng.rand()
        #demand =  scipy.stats.truncnorm((0 - mean) / var, np.inf, loc=mean, scale=var).ppf(sample) #self.mean + scipy.stats.norm.ppf(1 - x * (1 - scipy.stats.norm.cdf(-self.mean/self.var))) # TODO: switch to truncnorm
        #backup_required = 3 * np.sqrt(var) # 99% chance of having enough power with 3 standard deviations of backup power, 
        action = { # most of these are unnecessary fillers leftover from newsvendor demo
            'type': 'market_demand',
            'asin': 1,
            'origin': None,
            'destination': None,
            'quantity': demand, # realistically, predicted and backup would be bid for ahead of time, but it makes no difference in the sim
            'predicted': mean,
            'backup': 0,
            'schedule': state['clock'],
        }
        logger.debug("Market bought {} units of power".format(demand))
        #logger.debug("Market demanded {} units of backup power".format(backup_required))
        actions.append(action)
        
        return actions
        