#!/usr/bin/env python3 
import numpy as np
import pandas as pd
from keras.layers import LSTM
from keras.layers import Dense
from xgboost import XGBRegressor
from keras.models import Sequential
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler


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
    def __init__(self, data, train_weeks, lr=0.20, depth=3, est=1000, 
        n_in=15, n_out=1):

        self.raw = np.reshape(data['Ground Truth'].values, (len(data), 1))
        self.size = len(self.raw) - train_weeks
        self.n_in = n_in
        self.n_out = n_out
        self.depth = depth
        self.eta = lr
        self.est = est

    def series_to_supervised(self, dropnan=True):

        df = pd.DataFrame(self.raw)
        cols = list()

        for i in range(self.n_in, 0, -1):
            cols.append(df.shift(i))
        for i in range(0, self.n_out):
            cols.append(df.shift(-i))

        agg = pd.concat(cols, axis=1)

        if dropnan:
            agg.dropna(inplace=True)

        self.X = agg.values

    def train_test_split(self):
        self.train, self.test = self.X[:-self.size, :], self.X[-self.size:, :]


    def xgboost_forecast(self, train, testX):

        train = np.asarray(train)
        trainX, trainy = train[:, :-1], train[:, -1]

        model = XGBRegressor(objective='reg:squarederror', n_estimators=self.est, 
            max_depth=self.depth, eta=self.eta, sampling_method='gradient_based')
        model.fit(trainX, trainy)
        yhat = model.predict(np.asarray([testX]))

        return yhat[0]

    def walk_forward_validation(self):

        self.series_to_supervised()
        self.predictions = list()
        self.train_test_split()
        history = [x for x in self.train]

        for i in range(len(self.test)):

            testX, testy = self.test[i, :-1], self.test[i, -1]
            yhat = self.xgboost_forecast(history, testX)
            self.predictions.append(yhat)
            history.append(self.test[i])

            print('>expected=%.1f, predicted=%.1f' % (testy, yhat))

        return self.test[:, -1], self.predictions


class lstm_model:
    def __init__(self, data, train_weeks, lb=3, bs=1, ep=500):
        self.raw = np.reshape(data['Ground Truth'].values, (len(data), 1)).astype('float32')
        self.size = train_weeks
        self.look_back = lb
        self.batch_size = bs
        self.epochs = ep
        
    
    def create_dataset(self, dataset):
        dataX, dataY = [], []
        for i in range(len(dataset) - self.look_back-1):
            a = dataset[i:(i + self.look_back), 0]
            dataX.append(a)
            dataY.append(dataset[i + self.look_back, 0])

        return np.array(dataX), np.array(dataY)

    def get_train_test_split(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        dataset = self.scaler.fit_transform(self.raw)

        train, test = dataset[0:self.size,:], dataset[self.size:len(dataset),:]

        trainX, self.trainY = self.create_dataset(train)
        testX, self.testY = self.create_dataset(test)

        self.trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
        self.testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

    def model_func(self):

        self.model = Sequential()
        self.model.add(LSTM(10, input_shape=(1, self.look_back)))
        self.model.add(Dense(1))
        self.model.compile(loss='mean_squared_error', optimizer='adam')

    def train_and_predict(self):

        self.get_train_test_split()
        self.model_func()

        self.model.fit(self.trainX, self.trainY, epochs=self.epochs, 
            batch_size=self.batch_size, verbose=2)
        # make and invert predictions
        testPredict = self.model.predict(self.testX)
        testPredict = self.scaler.inverse_transform(testPredict)
        testY = self.scaler.inverse_transform([self.testY])
        
        return testY[0], testPredict.flatten()