#!/usr/bin/env python3 
import os
import click
import pandas as pd

def read_data(data, covid='before'):


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


def arrange_data_model(df, product, prod_type):

    df_prod = df[(df['Descripcion Sub-Familia Articulos'] == product) & \
        (df['Tipo de Producto'] == prod_type)]
    import pdb;pdb.set_trace()
    el_no_dis = df_prod[df_prod['Descuento aplicado'] < 40]

    df_tot = df_prod.groupby(['year', 'week']).apply(
            lambda x: x['Cantidad Pedida'].sum()).reset_index()

    df_tot['year_week'] = df_tot['year'].astype(str) + '_' + df_tot['week'].astype(str)

    df_no_dis = el_no_dis.groupby(['year', 'week']).apply(
            lambda x: x['Cantidad Pedida'].sum()).reset_index()

    df_no_dis['year_week'] = df_no_dis['year'].astype(str) + '_' + df_no_dis['week'].astype(str)

    df_no_dis.drop(['year', 'week'], axis=1, inplace=True)
    df_tot.drop(['year', 'week'], axis=1, inplace=True)

    both = df_tot.merge(df_no_dis, on='year_week', how='outer')
    both.columns = ['Actual', 'Date', 'Ground Truth']

    return both, df_prod['Descripcion Sub-Familia Articulos'].unique()[0], prod_type




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
    type=click.Choice(['ARIMA', 'GBM', 'LSTM']),
    help='choose ML model to perform the analysis'
)
@click.option(
    '-o', '--output', help='Path to save file'
)
def main(data, product_subfamily, product_type, covid, model_type, output):

    df = read_data(data, covid)

    df_model = arrange_data_model(df, product_subfamily, product_type)


    import pdb;pdb.set_trace()
    



if __name__ == '__main__':
    main()