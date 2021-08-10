## Imports

import pandas as pd
import numpy as np
from functools import reduce

## Constants

ANSWER_COLUMNS = ['Codes Favorite', 'Codes Least Favorite', 'Codes Updates', 'Codes Tutorial Favorite', 'Codes Tutorial Least Favorite'] 
def ADD(a, b): return a + b

## Reading

def clean_df(df_withna):
    df = df_withna.fillna("")
    def clean_series(series):
        def clean_item(item):
            split_item = item.replace(' ', '')\
                             .replace('/', '')\
                             .upper()\
                             .split(',')
            return list(filter(lambda list_item: list_item != "", split_item))
        return series.map(clean_item)

    for ans_col in ANSWER_COLUMNS:
        df[ans_col] = clean_series(df[ans_col])

    return df

def clean_and_read(filename): return clean_df(pd.read_csv(filename, sep='\t'))

BASENAME = "data/"
filenames = ["C1-v4.tsv", "C2-v4.tsv", "C3-v4.tsv"]
full_filenames = map(lambda filename: f'{BASENAME}{filename}', filenames)

coder_dfs = list(map(clean_and_read, full_filenames))

## Combining

def combine_dfs(*dfs):
    new_df = pd.DataFrame()
    new_df['Game'] = dfs[0]['Game']
    for ans_col in ANSWER_COLUMNS:
        new_df[ans_col] = reduce(ADD, [df[ans_col] for df in dfs])
    return new_df

combined_df = combine_dfs(*coder_dfs)

## Analysis

def dump_df_info(df_name, df):
    def value_information(series): return pd.Series(reduce(ADD, series)).value_counts().drop("NA")

    print(f'== INFORMATION FOR {df_name.upper()} == \n')
    for ans_col in ANSWER_COLUMNS:
        print(ans_col)
        print(value_information(df[ans_col]))
        print()

grouped_by_game = combined_df.groupby("Game")

# @JOSH LOOK AT THESE TWO LINES
dump_df_info("Foldit", grouped_by_game.get_group('Foldit'))
# dump_df_info("all data", combined_df)

print("all games:")
print(grouped_by_game.groups.keys())
