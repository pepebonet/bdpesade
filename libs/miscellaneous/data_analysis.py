#!/usr/bin/env python3 
import os
import click
import pickle
import pandas as pd

import plots as pl


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
@click.option(
    '-d', '--data', required=True, help='tsv file containing the data'
)
@click.option(
    '-o', '--output', help='Path to save file'
)
def main(df, output):
    #SCRIPT SHOULD FINISH HERE
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