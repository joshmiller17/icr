## Imports

import pandas as pd
import numpy as np
from functools import reduce

## Constants

ANSWER_COLUMNS = ['Codes Favorite', 'Codes Least Favorite', 'Codes Updates', 'Codes Tutorial Favorite', 'Codes Tutorial Least Favorite'] 
def ADD(a, b): return a + b

## Reading

def clean_df(df_withna_with_invalid):
    df_with_invalid = df_withna_with_invalid.fillna("")
    df = df_with_invalid[df_with_invalid['Valid'] == 'Yes']
    def clean_series(series):
        def clean_item(item):
            split_item = item.replace(' ', '')\
                             .replace('/', '')\
                             .upper()\
                             .split(',')
            return list(filter(None, split_item))
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

def dump_df_info(df_name, df, as_csv):
    def dump_series_info(series_name, series):
        reduced_list         = list(filter(lambda code: code != "NA", reduce(ADD, series)))
        num_codes            = len(reduced_list)
        values               = pd.Series(reduced_list).value_counts()
        value_df             = pd.DataFrame(values).rename({0: "Counts"}, axis=1)
        value_df["Percents"] = value_df["Counts"] / num_codes * 100
        print(f'{series_name}\n')
        print(f'{value_df.to_csv() if as_csv else value_df}\n')
        print(f'num codes: {num_codes}\n')

    print(f'== INFORMATION FOR {df_name.upper()} == \n')

    for ans_col in ANSWER_COLUMNS:
        dump_series_info(ans_col, df[ans_col])

    dump_series_info("All columns for this dataframe combined",
                     pd.concat([df[ans_col] for ans_col in ANSWER_COLUMNS]))

grouped_by_game = combined_df.groupby("Game")

## Output functions

def dump_all():
    dump_df_info("all data", combined_df, False)
    dump_df_info("all data", combined_df, True)

def dump_by_game():
    for name, df in grouped_by_game:
        if name != '':
            dump_df_info(name, df, False)
    for name, df in grouped_by_game:
        if name != '':
            dump_df_info(name, df, True)

def dump_combined_except(*games_to_exclude):
    filtered_df = combined_df[combined_df['Game'].map(lambda game: game not in games_to_exclude)]
    dump_df_info(f"All data combined, except for games {games_to_exclude}", filtered_df, True)
    dump_df_info(f"All data combined, except for games {games_to_exclude}", filtered_df, False)

# @JOSH here you are
dump_combined_except("Foldit")
dump_combined_except("Foldit", "EteRNA", "EyeWire")

# @JOSH if you want these as well
# dump_all()
# dump_by_game()

print(f"Games List: {grouped_by_game.groups.keys()}")
