import pandas as pd


FILE_NAME = 'data/cleaned/virus.csv'


def clean(df):
    # No.129-131 => 2 (Case number to case count)
    df['Case Count'] = df['Case']\
        .str[3:]\
        .str.split('-')\
        .apply(lambda a: 
            int(a[1]) - int(a[0]) if len(a) == 2 else 1)
    # Format Date column
    df.Date = df.Date.str.cat(['/2020' for _ in range(len(df))])
    df.Date = pd.to_datetime(df.Date)
    return df


if __name__ == "__main__":
    df = pd.read_csv('data/raw/virus.csv')
    df = clean(df)
    df.to_csv(FILE_NAME, index=False)
