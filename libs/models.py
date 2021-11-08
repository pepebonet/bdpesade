

#!/usr/bin/env python3 
from statsmodels.tsa.arima.model import ARIMA


class arima_model:
    def __init__(self, data, train_weeks, P=8, D=1, Q=1):
        self.size = train_weeks
        self.p = P
        self.d = D
        self.q = Q
        self.X = data['Ground Truth'].values

    def split_train_test(self):
        self.train, self.test = self.X[0:self.size], self.X[self.size:len(self.X)]
        self.history = [x for x in self.train]
        self.predictions = list()

    def train_model(self):

        self.split_train_test()

        for t in range(len(self.test)):
            model = ARIMA(self.history, order=(self.p, self.d, self.q))
            model_fit = model.fit()
            output = model_fit.forecast()
            yhat = output[0]
            self.predictions.append(yhat)
            obs = self.test[t]
            self.history.append(obs)

        return self.test, self.predictions

    
class gbm_model:
    def __init__(self, train_weeks):
        pass


class lstm_model:
    def __init__(self, train_weeks):
        pass