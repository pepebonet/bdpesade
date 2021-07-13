#!/usr/bin/env python3 

import click
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


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

    return df


#TODO <JB> This snippet takes nans away, is that what we want?
def classify_products(df):
    super_fresh = df[df['Diferencia_caducidad'] < 15]
    super_fresh['Tipo_Producto'] = 'Super Fresco'
    fresh = df[(df['Diferencia_caducidad'] >= 15) & \
        (df['Diferencia_caducidad'] <= 60)]
    fresh['Tipo_Producto'] = 'Fresco'
    dry = df[df['Diferencia_caducidad'] > 60]
    dry['Tipo_Producto'] = 'Seco'

    return pd.concat([super_fresh, fresh, dry])


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


def plot_groups(df):
    sns.set(rc={'figure.figsize':(7,5)})
    sns.set_style('whitegrid')

    ax = sns.barplot(data=df, x='Relative_counts', y='Descuento', 
        hue='Tipo_Producto', hue_order=['Seco', 'Fresco', 'Super Fresco'])

    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('discount_and_product.png')
    plt.close()


def plot_subgroups(df):
    sns.set(rc={'figure.figsize':(7,5)})
    sns.set_style('whitegrid')

    for i, j in df.groupby('Descuento'):
        ax = sns.barplot(data=j, x='Relative_counts', y='Descuento', 
            hue='Tipo_Producto', hue_order=['Seco', 'Fresco', 'Super Fresco'])

        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig('discount_and_product_{}.png'.format(i))
        plt.close()


@click.command(short_help='explore input data valcoiberia')
@click.option('-d', '--data', required=True, help='tsv file containing the data')
@click.option('-o', '--output', help='Path to save file')
def main(data, output):
    #load the data
    df = pd.read_csv(data, sep='\t') 

    #Remove all coluns that contain only nans
    df = df.dropna(axis=1, how='all') 

    #Remove all columns with more than 1M nans, with nuniques per column < 5
    # and with value counts for the largest value larger than 1M
    df = explore_columns(df)

    #drop columns that have the same info in other columns
    df = df.drop(['fam_codi'], axis=1)

    #Obtain the days that takes to the product to expire
    df = date_engineering(df)

    #Classify products based on the days to expire in three groups
    #Super fresh, fresh and dry
    df = classify_products(df)

    df = group_by_discount_section(df)

    #Generate plots
    plot_groups(df)
    plot_subgroups(df)


if __name__ == '__main__':
    main()