import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from pathlib import Path
import os

# import the data from github
# database url
url = 'https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2022/2022-01-18/chocolate.csv'

# read in csv file
chocolate_rating = pd.read_csv(url)

# create database
db_path = Path('chocolate.db')
if not db_path.exists():
    print(f'Data base {db_path} not found, created the database. 📊')

    # connect to database and create the data table
    with sqlite3.connect(db_path) as con:
        chocolate_rating.to_sql('chocolate_rating', con, if_exists='replace', index=False)
        print('Data table chocolate_rating has been created. 🧮')

else:
    print('Database already exists. 🤓')

# find the avarage rating per cacoa percentage
def rating_percentage():
    with sqlite3.connect(db_path) as con:
        query = '''
        SELECT cocoa_percent, rating
        FROM chocolate_rating
        '''
    df = pd.read_sql_query(query, con)
 
 # Ensure cocoa_percent is numeric
    df['cocoa_percent'] = df['cocoa_percent'].str.replace('%', '').astype(float)

    # Group by cocoa percent and calculate mean + std
    summary = df.groupby('cocoa_percent')['rating'].agg(['mean', 'std']).reset_index()
    print(summary)

def flav_char():
    with sqlite3.connect(db_path) as con:
        query = '''
        SELECT company_manufacturer, country_of_bean_origin, cocoa_percent, most_memorable_characteristics, rating
        FROM chocolate_rating
        WHERE most_memorable_characteristics LIKE '%nutty%'
        '''
    
    df = pd.read_sql_query(query, con)

    # save results into a new table called nutty_chocolates
    with sqlite3.connect(db_path) as con:
        df.to_sql("nutty_chocolates", con, if_exists="replace", index=False)
        print(f"Table 'nutty_chocolates' created/updated in {db_path} ({len(df)} rows)")

    # preview results
    if not df.empty:
        print(df.to_string(index=False))
    else:
        print("No rows matched the filter (nutty).")

def chart_origin_pie():
    with sqlite3.connect(db_path) as con:
        query = '''
        SELECT country_of_bean_origin
        FROM chocolate_rating
        '''
    df = pd.read_sql_query(query, con)

    # group by origin and find percentage
    origin_counts = df.value_counts().sort_index()

    # create a pie chart 
    plt.figure(figsize=(10, 10))
    plt.pie(origin_counts, labels=origin_counts.index,
            autopct='%1.1f%%', startangle=140)
    plt.title('Percentage by Origin of the Beans')
    plt.show()

def chart_origin_bar():
    with sqlite3.connect(db_path) as con:
        query = '''
        SELECT country_of_bean_origin
        FROM chocolate_rating
        '''
    df = pd.read_sql_query(query, con)

    # Count frequencies per origin (clean up blanks/NaNs)
    counts = (
        df['country_of_bean_origin']
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace({"": "Unknown"})
        .value_counts()
        .sort_values(ascending=False)
    )

    # create bar chart 
    plt.figure(figsize=(10, 6))
    plt.bar(counts.index, counts.values)
    plt.xticks(rotation=90)
    plt.xlabel('Origin')
    plt.ylabel('Total')
    plt.title('Frequency of Bean Country of Origin')
    plt.tight_layout()
    plt.show()


# rating_percentage()
# flav_char()
# chart_origin_pie()
# chart_origin_bar()