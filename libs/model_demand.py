#!/usr/bin/env python3 
import os
import sys
import click
import pandas as pd
from math import sqrt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

sys.path.append('./')
import libs.models as md


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


def get_error_measurements(test, predictions, df):

    rmse_m = sqrt(mean_squared_error(test, predictions))
    mae_m = mean_absolute_error(test, predictions)

    rmse_a = sqrt(mean_squared_error(test, df['Actual'].tolist()[-len(test):]))
    mae_a = mean_absolute_error(test, df['Actual'].tolist()[-len(test):])
    
    return rmse_m, mae_m, rmse_a, mae_a


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
    '-pa', '--p_arima', default=8, 
    help='p parameter of the arima model'
)
@click.option(
    '-da', '--d_arima', default=1, 
    help='d parameter of the arima model'
)
@click.option(
    '-qa', '--q_arima', default=1, 
    help='q parameter of the arima model'
)
@click.option(
    '-tw', '--train_weeks', default=22, 
    help='number of weeks to get the model trained'
)
@click.option(
    '-o', '--output', help='Path to save file'
)
def main(data, product_subfamily, product_type, covid, model_type, train_weeks,
    p_arima, d_arima, q_arima, output):

    df = read_data(data, covid)

    df_model = arrange_data_model(df, product_subfamily, product_type)

    if model_type == 'arima':
        test, predictions = md.arima_model(
            df_model, train_weeks, p_arima, d_arima, q_arima).train_model()

    elif model_type == 'gbm':
        predictions = md.gbm_model(df_model, train_weeks).train_model()
    
    else:
        predictions = md.lstm_model(df_model, train_weeks).train_model()

    rmse_m, mae_m, rmse_a, mae_a = get_error_measurements(
        test, predictions, df_model)
    import pdb;pdb.set_trace()
    

if __name__ == '__main__':
    main()