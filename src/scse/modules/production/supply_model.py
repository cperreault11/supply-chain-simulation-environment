import GPy
import os


class SupplyModel():

    def __init__(self, model_name, mean=0.0, var=1.0, offset=0.0, scale=1.0):
        self.model = GPy.models.GPRegression(
            f'src/scse/modules/demand/{model_name}.zip')
        self.mean = mean
        self.var = var
        self.offset = offset
        self.scale = scale
        self.restart()

    def restart(self):
        self.last_prediction = np.random.normal(self.mean, self.var)

    def predict(self, date):
        input = np.array(
            [date.weekday()/6.0, date.month()/11.0, self.last_prediction])
        self.last_prediction = self.model.predictive_posterior(input)[0]
        return self.last_prediction * self.scale + self.offset
