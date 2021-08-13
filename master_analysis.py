## Imports

import pandas as pd
import numpy as np
from functools import reduce

## Reading

def validate_df(df):
    # Keep only valid rows
    age = df['What is your age?'].fillna(0)
    adults = (age >= 18) & (age <= 98)
    return df[adults]

df = validate_df(pd.read_csv("data/master.tsv", sep='\t'))

## Num games
print(df['Which game are you responding for?'].value_counts())
## Ages
print(df['What is your age?'].mean())
print(df['What is your age?'].std())
## Education
print(df['How much education do you have about the topic of the game?'].value_counts())
## Expertise
print(df['What is your level of expertise with this game?'].value_counts())
## Frequency
print(df['How often do you play games?'].value_counts())
## Genre
def splitstrip(string):
    return list(map(lambda s: s.strip(), string.split(",")))
genres = df['What kind of games do you play? Check all that apply.'].fillna("").map(splitstrip)

crunched_genres = pd.Series(reduce(lambda x, y: x + y, genres))
print(crunched_genres.value_counts())
