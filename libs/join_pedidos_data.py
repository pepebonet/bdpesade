#!/usr/bin/envs python3 

import os
import click
import pandas as pd 
from tqdm import tqdm

from openpyxl import load_workbook



@click.command(short_help='join and clean data valcoiberia')
@click.option('-fd', '--folder_data', required=True, help='folder with data')
@click.option('-o', '--output', help='Path to save file', default='')
def main(folder_data, output):

    df_final = pd.DataFrame()

    for file in tqdm(os.listdir(folder_data)):

        wb = load_workbook(filename=os.path.join(folder_data, file))
        ws = wb.active
        df = pd.DataFrame(ws.values)
        df = df.rename(columns=df.iloc[0]).drop(axis=0, index=0)
        df_final = pd.concat([df_final, df])

    df_final.to_csv(
        os.path.join(folder_data, 'pedidos_all.tsv'), sep='\t', index=None
    )

if __name__ == '__main__':
    main()