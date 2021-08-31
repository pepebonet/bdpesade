#!/usr/bin/env python3 
import os
import click
import pandas as pd

import plots as pl


def explore_columns(df):
    for col in df:
        if (df[col].isna().sum() > 1000000) or (df[col].nunique() <= 5) \
            or (df[col].value_counts().values[0] > 1000000):
            df = df.drop([col], axis=1)
            
    return df


def date_engineering(df):
    df['Fecha_caducidad'] = pd.to_datetime(df['lot_fecha_caducidad'])
    df['Fecha_alta'] = pd.to_datetime(df['lot_fecha_alta'])
    df['Diferencia_caducidad'] = (df['Fecha_caducidad'] - df['Fecha_alta']).dt.days
    df = df.drop(['Fecha_alta', 'Fecha_caducidad', \
        'lot_fecha_caducidad', 'lot_fecha_alta'], axis=1)

    return df


#TODO <JB> This snippet takes nans away, is that what we want?
def classify_products(df):
    Ultra_fresh = df[df['Diferencia_caducidad'] < 15]
    Ultra_fresh['Tipo_Producto'] = 'Ultra Fresco'
    fresh = df[(df['Diferencia_caducidad'] >= 15) & \
        (df['Diferencia_caducidad'] <= 60)]
    fresh['Tipo_Producto'] = 'Fresco'
    dry = df[df['Diferencia_caducidad'] > 60]
    dry['Tipo_Producto'] = 'Seco'

    return pd.concat([Ultra_fresh, fresh, dry])


def group_by_discount_section(df):

    df_toplot = pd.DataFrame()
    for i, j in [(-1,20), (20,40), (40,60), (60, 100)]:
        int_df = pd.DataFrame(df[(df['lin_dte'] > i) & \
            (df['lin_dte'] <= j)].groupby('Tipo_Producto').apply(
                lambda x: x.shape[0])).reset_index()
        if i == -1:
            int_df['Descuento'] = '0-{}%'.format(j)
        else:
            int_df['Descuento'] = '{}-{}%'.format(i, j)
        df_toplot = pd.concat([df_toplot, int_df])

    rel_df = pd.DataFrame()
    for k, l in df_toplot.groupby('Tipo_Producto'):
        l['Relative_counts'] = l[0] / df['Tipo_Producto'].value_counts()[k]
        rel_df = pd.concat([rel_df, l])

    return rel_df


def limpiar_clientes(df, categoria_cliente):

    limp_clientes = pd.read_csv(categoria_cliente, sep='\t')
    clientes = limp_clientes[['cli_rao', 'Tipología cliente ok']]
    merge_clientes = pd.merge(df, clientes, how='inner', on='cli_rao')

    df = merge_clientes[merge_clientes['Tipología cliente ok'] != 'quitar'].drop(
        ['Tipología cliente ok'], axis=1
    )

    return df


def group_discount_50(df):
    df_toplot = pd.DataFrame()
    for i, j in [(0,49), (50, 100)]:
        
        int_df = pd.DataFrame(df[(df['lin_dte'] >= i) & \
            (df['lin_dte'] <= j)].groupby(['Tipo_Producto', 'year']).apply(
                lambda x: x.shape[0])).reset_index()

        int_df['Descuento'] = '{}-{}%'.format(i,j)
        df_toplot = pd.concat([df_toplot, int_df])

    rel_df = pd.DataFrame()
    for k, l in df_toplot.groupby(['Tipo_Producto', 'year']):
        l['Relative_counts'] = l[0] / df[(df['Tipo_Producto'] == k[0]) & (df['year'] == k[1])].shape[0]
        rel_df = pd.concat([rel_df, l])

    return rel_df


def analyze_products(df):
    df = df[df['lin_dte'] >= 50]
    return df.groupby(['Tipo_Producto', 'sub_descrip']).apply(
        lambda x: x.shape[0]).reset_index()


@click.command(short_help='explore input data valcoiberia')
@click.option('-d', '--data', required=True, help='tsv file containing the data')
@click.option('-cc', '--categoria_cliente', default='', help='limpieza clientes')
@click.option('-o', '--output', help='Path to save file')
def main(data, categoria_cliente, output):
    #load the data
    df = pd.read_csv(data, sep='\t', nrows=10000000) 
    
    #Remove all coluns that contain only nans
    df = df.dropna(axis=1, how='all') 

    #Remove all columns with more than 1M nans, with nuniques per column < 5
    # and with value counts for the largest value larger than 1M
    df = explore_columns(df)

    #drop columns that have the same info in other columns
    df = df.drop(['fam_codi'], axis=1)

    if categoria_cliente:
        df = limpiar_clientes(df, categoria_cliente)

    #TODO one of the things that can be done is to delete those columns with many unique
    #so far not all columns are important for sure

    #Obtain the days that takes to the product to expire
    df = date_engineering(df)
    df['year'] = pd.DatetimeIndex(df['cpa_datalb']).year

    #Classify products based on the days to expire in three groups
    #Ultra fresh, fresh and dry
    df = classify_products(df)
    import pdb;pdb.set_trace()
    #get different sections of discount
    rel_df = group_by_discount_section(df)

    #split discounts only in two to analyze changes within time 
    df_discount = group_discount_50(df)
    df_discount.to_csv(os.path.join(output, 'discount_50.tsv'), sep='\t', index=None)
    
    df_products = analyze_products(df)

    #Generate plots
    pl.plot_groups(rel_df)
    pl.plot_subgroups(rel_df)
    pl.plot_evolution_discount(df_discount, output)
    pl.plot_products_discounted(df_products, output)


if __name__ == '__main__':
    main()