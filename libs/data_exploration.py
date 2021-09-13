#!/usr/bin/env python3 
import os
import click
import pickle
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


def limpiar_clientes(df, categoria_cliente):

    limp_clientes = pd.read_csv(categoria_cliente, sep='\t')
    clientes = limp_clientes[['cli_rao', 'Tipología cliente ok']]
    merge_clientes = pd.merge(df, clientes, how='inner', on='cli_rao')

    df = merge_clientes[merge_clientes['Tipología cliente ok'] != 'quitar'].drop(
        ['Tipología cliente ok'], axis=1
    )

    return df


def remove_duplicated_columns(df):

    ncol = len(df.columns)
    in_col = df.columns
    
    for i in range(ncol):
        if in_col[i] in df:
            for j in range(i + 1, ncol):
                if in_col[j] in df:
                    to_assert = df[in_col[i]].values == df[in_col[j]].values
                    if to_assert.all():
                        df.drop([in_col[j]], axis=1, inplace=True)
    
    return df


def clean_df(df, dict_path):

    with open(dict_path, 'rb') as handle:
        dict_names = pickle.load(handle)
   
    for i, j in dict_names.items():

        if j == 'delete':
            df.drop([i], axis=1, inplace=True)
        else:
            df.rename(columns={i: j}, inplace=True)

    return df


def save_outputs(df, output):

    out_file = os.path.join(output, 'final_cleaned_data.tsv')
    df.to_csv(out_file, sep='\t', index=None)


@click.command(short_help='explore input data valcoiberia')
@click.option(
    '-d', '--data', required=True, help='tsv file containing the data'
)
@click.option(
    '-cc', '--categoria_cliente', default='', help='limpieza clientes'
)
@click.option(
    '-cn1', '--clean_names_1', default='', 
    help='list to rename or delete certain columns'
)
@click.option(
    '-cn2', '--clean_names_2', default='', 
    help='list to rename or delete certain columns'
)
@click.option(
    '-nd', '--names_dict', default='', 
    help='dict containing column names to change or delete '
)
@click.option(
    '-o', '--output', help='Path to save file'
)
def main(data, categoria_cliente, clean_names_1, clean_names_2, names_dict, output):

    # Load the data
    df = pd.read_csv(data, sep='\t', nrows=2000000) 
    
    # Remove all columns that contain only nans
    df = df.dropna(axis=1, how='all') 
    
    # Remove all columns with more than 1M nans, with nuniques per column < 5
    # and with value counts for the largest value larger than 1M
    df = explore_columns(df)

    # Drop columns that have the same info in other columns
    df = df.drop(['fam_codi'], axis=1)

    if categoria_cliente:
        df = limpiar_clientes(df, categoria_cliente)

    #Obtain the days that takes to the product to expire
    df = date_engineering(df)
    df['year'] = pd.DatetimeIndex(df['cpa_datalb']).year

    #Classify products based on the days to expire into Ultra fresh, fresh and dry
    df = classify_products(df)

    df = clean_df(df, names_dict)

    df = remove_duplicated_columns(df)
    
    #save outputs
    save_outputs(df, output)
    import pdb;pdb.set_trace()
    

if __name__ == '__main__':
    main()