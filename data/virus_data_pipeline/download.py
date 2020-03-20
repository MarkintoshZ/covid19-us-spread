from scrap import retrieve_data
from clean import clean

FILE_NAME = 'data/cleaned/virus.csv'

if __name__ == "__main__":
    df = retrieve_data()
    df = clean(df)
    df.to_csv(FILE_NAME, index=False)