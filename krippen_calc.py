## Imports

import pandas as pd
import numpy as np
from functools import reduce
from tqdm import tqdm
from krippendorff import alpha

## Constants

ANSWER_COLUMNS = ['Codes Favorite', 'Codes Least Favorite', 'Codes Updates', 'Codes Tutorial Favorite', 'Codes Tutorial Least Favorite'] 
CODES = ["PATHPACE", "PORT", "IGE", "INTPUZ", "ACCESS", "SOC", "BRE", "TASKQUAL", "GAMIFICATION", "PUFQOL", "IAI", "SOFTWARE", "PARATEXTS", "DEVCOMM", "SCICOMM", "REALSCI", "USOG", "HARD", "CONFUSED", "INSTRUCTIONS", "UNK", "NA"]
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
        return series.map(clean_item).map(lambda item: ["NA"] if len(item) == 0 else item)

    for ans_col in ANSWER_COLUMNS:
        df[ans_col] = clean_series(df[ans_col])

    return df.reset_index(drop=True)

def clean_and_read(filename): return clean_df(pd.read_csv(filename, sep='\t'))

BASENAME = "data/"
filenames = ["C1-v4.tsv", "C2-v4.tsv", "C3-v4.tsv"]
full_filenames = map(lambda filename: f'{BASENAME}{filename}', filenames)

coder_dfs = list(map(clean_and_read, full_filenames))

## Create krippen_df

def has_code(df, column, row_idx, code):
    return int(code in df[column][row_idx])

krippen_df = pd.DataFrame()
for ans_col in tqdm(ANSWER_COLUMNS):
    for code in CODES:
        for idx in range(len(coder_dfs[0])):
            col_name = f"{ans_col}_{code}_{idx}"
            krippen_df[col_name] = [has_code(df, ans_col, idx, code) for df in coder_dfs]

## Run krippendorf calculation

print("=== ALPHA ===")
print(alpha(reliability_data=krippen_df.to_numpy()))
