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

class DemandSim():
    def __init__(self):
        path = os.path.abspath("src/scse/modules/demand/demand-sim.zip")
        self.gpy_model = GPy.models.GPRegression.load_model(path)

    def predict(self, date):
        day_of_week = normalize_single_feature(date.weekday(), 0, 6)
        _, week_of_year, _ = date.isocalendar() 
        week_of_year = normalize_single_feature(week_of_year, 1, 53)
        x = np.array([week_of_year, day_of_week])
        X = np.array([x])
        y = self.gpy_model.posterior_samples(X, size=1)
        return y[0][0][0] * 500000


class DemandPred():
    def __init__(self):
        path = os.path.abspath("src/scse/modules/demand/demand-pred.zip")
        self.gpy_model = GPy.models.GPRegression.load_model(path)

    def predict(self, date, previous_value):
        day_of_week = normalize_single_feature(date.weekday(), 0, 6)
        _, week_of_year, _ = date.isocalendar() 
        week_of_year = normalize_single_feature(week_of_year, 1, 53)
        x = np.array([week_of_year, day_of_week, previous_value / 500000.0])
        X = np.array([x])
        y = self.gpy_model.predict(X)
        return (y[0][0][0] * 500000, math.sqrt(y[1][0][0]) * 500000)

import logging
logger = logging.getLogger(__name__)
VAR = 5 # could set these with run params if we want
class NormalPowerDemand(Agent):
    def __init__(self, run_parameters):
        simulation_seed = run_parameters['simulation_seed']
        self._rng = np.random.RandomState(simulation_seed)
        self.mean = run_parameters['mean_demand']
        self.var = VAR
        self.demand_pred = DemandPred()
        self.demand_sim = DemandSim()

    def get_name(self):
        return 'demand_generator'

    def reset(self,context,state):
        return None

    def compute_actions(self, state):
        previous_date = state['date_time'] + datetime.timedelta(days=-1)
        previous_demand = self.demand_sim.predict(previous_date)
        demand, std_dev = self.demand_pred.predict(state['date_time'], previous_demand)
       
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
            'quantity': demand + std_dev, 
            'predicted': mean,
            'backup': 0,
            'schedule': state['clock'],
        }
        logger.debug("Market bought {} (pred) + {} (stddev) = {} units of power".
            format(demand, std_dev, demand + std_dev))
        #logger.debug("Market demanded {} units of backup power".format(backup_required))
        actions.append(action)
        
        return actions
        