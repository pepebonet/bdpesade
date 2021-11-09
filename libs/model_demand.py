#!/usr/bin/env python3 
import os
import sys
import click
import pandas as pd
from math import sqrt
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

    return pd.DataFrame([[rmse_m, rmse_a, 'RMSE'],[mae_m, mae_a, 'MAE']], 
        columns=['Model', 'Valcoiberia', 'Measurement'])


def save_outputs(df_errors, df_model, predictions, product_subfamily, 
    product_type, model_type, output):
    
    product_subfamily = product_subfamily.replace(' ', '_')
    file = '{}_{}_{}'.format(product_subfamily, product_type, model_type)

    df_errors.to_csv(
        os.path.join(output, 'errors_{}.tsv'.format(file)), sep='\t', index=None)
    
    df_model.to_csv(
        os.path.join(output, 'data_model_{}.tsv'.format(file)), sep='\t', index=None)
    
    preds = pd.DataFrame(predictions, columns=['Predictions'])
    preds.to_csv(
        os.path.join(output, 'preds_model_{}.tsv'.format(file)), sep='\t', index=None)


@click.command(short_help='explore input data valcoiberia')
@click.option(
    '-dt', '--data', default='', help='tsv file containing the data'
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
    '-lrb', '--learning_rate_boost', default=0.2, 
    help='learning rate for the gradient boosting model'
)
@click.option(
    '-db', '--depth_boost', default=3, 
    help='depth of the trees in the GBM'
)
@click.option(
    '-eb', '--est_boost', default=1000, 
    help='number of estimators in the GBM'
)
@click.option(
    '-ib', '--in_boost', default=15, 
    help='Number of lag observations as input'
)
@click.option(
    '-ob', '--out_boost', default=1, 
    help='Number of observations as output'
)
@click.option(
    '-lb', '--look_back', default=3, 
    help='lag values to use in the lstm'
)
@click.option(
    '-bs', '--batch_size', default=1, 
    help='size for every batch to train the lstm'
)
@click.option(
    '-ep', '--epochs', default=500, 
    help='number of epochs to train the lstm'
)
@click.option(
    '-tw', '--train_weeks', default=22, 
    help='number of weeks to get the model trained'
)
@click.option(
    '-o', '--output', help='Path to save file'
)
def main(data, product_subfamily, product_type, covid, model_type, train_weeks,
    p_arima, d_arima, q_arima, learning_rate_boost, depth_boost, est_boost,
    in_boost, out_boost, look_back, batch_size, epochs, output):

    df = read_data(data, covid)

    df_model = arrange_data_model(df, product_subfamily, product_type)

    if model_type == 'arima':
        test, predictions = md.arima_model(
            df_model, train_weeks, p_arima, d_arima, q_arima).train_model()

    elif model_type == 'gbm':
        test, predictions = md.gbm_model(df_model, train_weeks, learning_rate_boost, 
            depth_boost, est_boost, in_boost, out_boost).walk_forward_validation()
    
    else:
        test, predictions = md.lstm_model(df_model, train_weeks, look_back, batch_size, 
            epochs).train_and_predict()

    df_errors = get_error_measurements(test, predictions, df_model)

    save_outputs(df_errors, df_model, predictions, product_subfamily, 
        product_type, model_type, output)
    

if __name__ == '__main__':
    main()