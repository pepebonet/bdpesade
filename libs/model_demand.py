#!/usr/bin/env python3 
import os
import click
import pandas as pd
from math import sqrt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

def read_data(data, covid):


    df = pd.read_csv(data, sep='\t')

    df['year'] = pd.to_datetime(df['Fecha_Albaran']).dt.year
    df['month'] = pd.to_datetime(df['Fecha_Albaran']).dt.month
    df['week'] = pd.to_datetime(df['Fecha_Albaran']).dt.week

    if covid == 'before':
        return df[df['year'] < 2020]
    
    else:
        df_2021 = df[(df['year'] == 2021) & (df['month'] < 5)]
        df_2020 = df[(df['year'] == 2020) & (df['month'] >= 9)]
        return pd.concat([df_2020, df_2021])


def get_ground_truth_and_actual(df_prod):
    df_tot = df_prod.groupby(['year', 'week']).apply(
            lambda x: x['Cantidad Pedida'].sum()).reset_index()

    df_tot['year_week'] = df_tot['year'].astype(str) + \
        '_' + df_tot['week'].astype(str)

    el_no_dis = df_prod[df_prod['Descuento aplicado'] < 40]
    
    df_no_dis = el_no_dis.groupby(['year', 'week']).apply(
            lambda x: x['Cantidad Pedida'].sum()).reset_index()

    df_no_dis['year_week'] = df_no_dis['year'].astype(str) + \
        '_' + df_no_dis['week'].astype(str)

    df_no_dis.drop(['year', 'week'], axis=1, inplace=True)
    df_tot.drop(['year', 'week'], axis=1, inplace=True)

    both = df_tot.merge(df_no_dis, on='year_week', how='outer')
    both.columns = ['Actual', 'Date', 'Ground Truth']

    return both


def arrange_data_model(df, product, prod_type):

    df_prod = df[(df['Descripcion Sub-Familia Articulos'] == product) & \
        (df['Tipo de Producto'] == prod_type)]

    df_model = get_ground_truth_and_actual(df_prod)

    return df_model


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


@click.command(short_help='explore input data valcoiberia')
@click.option(
    '-da', '--data', default='', help='tsv file containing the data'
)
@click.option(
    '-ps', '--product_subfamily', default='MOZZARELLA PER PIZZA',
    help='choose product subfamily to run the forecast on'
)
@click.option(
    '-pt', '--product_type', default='Fresco',
    type=click.Choice(['Fresco', 'Seco', 'Ultra Fresco']),
    help='choose type of product'
)
@click.option(
    '-c', '--covid', default='after',
    type=click.Choice(['before', 'after']),
    help='choose the time stamp to perform the analysis (before or after covid)'
)
@click.option(
    '-m', '--model_type', required=True,
    type=click.Choice(['arima', 'gbm', 'lstm']),
    help='choose ML model to perform the analysis'
)
@click.option(
    '-tw', '--train_weeks', default=-1, 
    help='number of weeks to get the model trained'
)
@click.option(
    '-o', '--output', help='Path to save file'
)
def main(data, product_subfamily, product_type, covid, model_type, train_weeks, 
    output):

    df = read_data(data, covid)

    df_model = arrange_data_model(df, product_subfamily, product_type)

    if model_type == 'arima':
        test, predictions = arima_model(df_model, train_weeks).train_model()

    elif model_type == 'gbm':
        predictions = gbm_model(df_model, train_weeks).train_model()
    
    else:
        predictions = lstm_model(df_model, train_weeks).train_model()

    get_error_measurements(test, predictions, df_model)
    import pdb;pdb.set_trace()
    

if __name__ == '__main__':
    main()