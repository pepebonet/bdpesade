#!/usr/bin/env python3 

import click
import pandas as pd


def explore_columns(df):
    for col in df.columns:
        if df[col].isna().sum() > 1000000:
            df = df.drop([col], axis=1)
        
        else:
            if df[col].nunique() <= 5:
                df = df.drop([col], axis=1)
            
    return df


def explore_unique(df):

    for col in df:
        if df[col].value_counts().values[0] > 1000000:
            import pdb;pdb.set_trace()


@click.command(short_help='explore input data valcoiberia')
@click.option('-d', '--data', required=True, help='tsv file containing the data')
@click.option('-o', '--output', help='Path to save file')
def main(data, output):
    #load the data
    df = pd.read_csv(data, sep='\t') 

    #Remove all coluns that contain only nans
    df = df.dropna(axis=1, how='all') 

    #Remove all columns with more than 1M nans and with nuniques per column < 5
    df = explore_columns(df)

    #drop columns that have the same info in other columns
    df = df.drop(['act_descrip', 'fam_codi', 'pai_codi', 'pai_intrastat'], axis=1)

    df = explore_unique(df)
    import pdb;pdb.set_trace()

if __name__ == '__main__':
    main()