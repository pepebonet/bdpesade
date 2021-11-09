#!/usr/bin/envs python3 

import os
import click
import pandas as pd 

from tqdm import tqdm
from openpyxl import load_workbook


@click.command(short_help='join and clean data valcoiberia')
@click.option('-fd', '--folder_data', required=True, help='folder with data')
@click.option('-o', '--output', help='Path to save file')
def main(folder_data, output):

    all_year_dfs = {}; labels = []
    for folder in [f.path for f in os.scandir(folder_data) if f.is_dir()]:
        df_year = pd.DataFrame(); year = folder.rsplit('/', 1)[-1]
        counter = 0
        for file in tqdm(os.listdir(folder)):
            wb = load_workbook(filename=os.path.join(folder, file))
            ws = wb.active
            df = pd.DataFrame(ws.values)
            df = df.rename(columns=df.iloc[0]).drop(axis=0, index=0)
            try:
                df.drop(['cpa_observ','cpa_obsser','lin_apliac','lin_observ',
                    'lin_nnumer','cpa_obsse2','art_observ'], axis=1, inplace=True)
            except:
                pass
            counter += 1
            label = '{}_{}'.format(year, counter)
            labels.append(label)
            all_year_dfs[label] = df
    

    col_names = all_year_dfs['2021_2'].columns
    for el in labels:
        all_year_dfs[el].columns = col_names

    final_df = pd.DataFrame()
    for i, j in all_year_dfs.items():
        final_df = pd.concat([final_df, j])

    final_df.to_csv(os.path.join(output, 'TotalSales.tsv'), sep='\t', index=None)


if __name__ == '__main__':
    main()