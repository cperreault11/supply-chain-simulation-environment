import GPy
import pickle
import numpy as np


class SupplyModel():

    def __init__(self, model_name, mean=0.0, var=1.0, offset=0.0, scale=1.0):
        model_file = f'src/scse/modules/production/{model_name}.pkl'
        with open(model_file, 'rb') as file:
            self.model = pickle.load(file)
        self.mean = mean
        self.var = var
        self.offset = offset
        self.scale = scale
        self.restart()

    def restart(self):
        self.last_prediction = np.random.normal(self.mean, self.var)

    def predict(self, date):
        input = np.array(
            [[date.timetuple().tm_yday, date.weekday()/6.0, self.last_prediction]])
        self.last_prediction = \
            self.model.posterior_samples(input, size=1)[0][0][0]
        return self.last_prediction * self.scale + self.offset
