#!/usr/bin/envs python3 

import os
import click
import pandas as pd 

from openpyxl import load_workbook



@click.command(short_help='join and clean data valcoiberia')
@click.option('-fd', '--folder_data', required=True, help='folder with data')
@click.option('-o', '--output', help='Path to save file')
def main(folder_data, output):

    all_year_dfs = {} 
    for folder in [f.path for f in os.scandir(folder_data) if f.is_dir()]:
        df_year = pd.DataFrame(); year = folder.rsplit('/', 1)[-1]
        
        for file in os.listdir(folder):
            wb = load_workbook(filename=os.path.join(folder, file))
            ws = wb.active
            df = pd.DataFrame(ws.values)
            df = df.rename(columns=df.iloc[0]).drop(axis=0, index=0)
            df_year = pd.concat([df_year, df])
            
        all_year_dfs[year] = df_year


if __name__ == '__main__':
    main()