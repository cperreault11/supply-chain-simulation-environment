import numpy as np
from scse.api.module import Agent
import scipy.stats
import GPy
import os
from IPython import embed
import math
import datetime

def normalize_single_feature(arr, arr_min, arr_max):
    return ((arr - arr_min)/(arr_max-arr_min))


class DemandModel():
    def __init__(self,max_demand):
        path = os.path.abspath("src/scse/modules/demand/demand-model.zip")
        self.gpy_model = GPy.models.GPRegression.load_model(path)
        self.max_demand = max_demand

    def predict(self, date, previous_value):
        day_of_week = normalize_single_feature(date.weekday(), 0, 6)
        _, week_of_year, _ = date.isocalendar() 
        week_of_year = normalize_single_feature(week_of_year, 1, 53)
        x = np.array([week_of_year, day_of_week, previous_value / self.max_demand])
        X = np.array([x])
        y = self.gpy_model.posterior_samples(X,size=1)[0][0][0]
        var = self.gpy_model.predict(X)[1][0]
        return (y * self.max_demand, math.sqrt(var) * self.max_demand)

import logging
logger = logging.getLogger(__name__)
VAR = 5 # could set these with run params if we want
class NormalPowerDemand(Agent):
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        #self.mean = run_parameters['mean_demand']
        #self.var = VAR
        self.previous_demand = np.random.normal(0.7, 0.1, 1)[0]*run_parameters['max_demand']
        self.demand_model = DemandModel(run_parameters['max_demand'])


    def get_name(self):
        return 'demand_generator'

    def reset(self,context,state):
        return None

    def compute_actions(self, state):
        demand, std_dev = self.demand_model.predict(state['date_time'], self.previous_demand)
        self.previous_demand = demand

        logger.debug("demand: " + str(demand) + ", std_dev: " + str(std_dev))

        actions = []
        x = self._rng.rand()
        # truncated normal, can't have negative demand
        #mean = self.mean # this can change by time series if we switch it to that
        #var = self.var # again, this can change by time series.
        #sample = self._rng.rand()
        #demand =  scipy.stats.truncnorm((0 - mean) / var, np.inf, loc=mean, scale=var).ppf(sample) #self.mean + scipy.stats.norm.ppf(1 - x * (1 - scipy.stats.norm.cdf(-self.mean/self.var))) # TODO: switch to truncnorm
        #backup_required = 3 * np.sqrt(var) # 99% chance of having enough power with 3 standard deviations of backup power, 
        
        quantity = demand + 2*std_dev 
        
        action = { # most of these are unnecessary fillers leftover from newsvendor demo
            'type': 'market_demand',
            'asin': 1,
            'origin': None,
            'destination': None,
            'sd': std_dev, 
            'predicted': demand,
            'quantity': demand, 
            'schedule': state['clock'],
        }
        #logger.debug("Market bought {} (pred) + 3x{} (stddev) = {} units of power".
        #    format(demand, std_dev, quantity))
        #logger.debug("Market demanded {} units of backup power".format(backup_required))
        actions.append(action)
        
        return actions
        