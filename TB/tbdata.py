import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os
import numpy as np 

# create variable for url
base_url = 'https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-11-18/who_tb_data.csv' 

# create pd for TB data
whotbdata = pd.read_csv(base_url)

#create database
db_name = 'WHOTB.db'

def create_tb_database(db_name):
    if not os.path.exists(db_name):
        print(f'Database not found, creating {db_name}. 🤓')
        with sqlite3.connect(db_name) as con:
            whotbdata.to_sql('tbdata', con, if_exists='replace', index=False)
            print(f"Database {db_name} created with table 'tbdata'. 👍")
    else:
            print('Database already exists. 🧮')

 # create_tb_database(db_name)

# create query for deaths per 100k in 2023
with sqlite3.connect(db_name) as con:
    query = '''
    SELECT e_mort_100k
    FROM tbdata
    WHERE year = 2023
    '''

# create dataframe from the query
    df = pd.read_sql_query(query, con)

# function to calculate average deaths per 100k in 2023
def avg_deaths_per_100k_2023(df):
    # ensure numeric and drop missing values
    values = pd.to_numeric(df['e_mort_100k'], errors='coerce').dropna()
    avg = values.mean()
    return avg

average_2023 = avg_deaths_per_100k_2023(df)
print(f"Average estimated TB deaths per 100k in 2023: {average_2023:.1f}")

# create query for top 20 countries for mortality rates
with sqlite3.connect(db_name) as con:
    query = '''
    SELECT country, e_mort_100k
    FROM tbdata
    WHERE year = 2023 AND e_mort_100k IS NOT NULL
    ORDER BY e_mort_100k DESC
    LIMIT 20
    '''
# create df from the query
    df = pd.read_sql_query(query, con)

# create a bar chart of countries with highest mortality
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(df['country'], df['e_mort_100k'], color='tomato', edgecolor='black')

ax.bar_label(bars, fmt='%.1f', padding=3, rotation=45, fontsize=9)

ax.set_ylabel('TB deaths per 100k')
ax.set_xlabel('Country')
ax.set_title('Top 20 Countries by TB Deaths per 100k (2023)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# create a table of 10 countries with lowest mortality 
with sqlite3.connect(db_name) as con:
    query = '''
    SELECT country, e_mort_100k
    FROM tbdata
    WHERE year = 2023 and e_mort_100k IS NOT NULL
    ORDER BY e_mort_100k ASC
    LIMIT 20
    '''

# create df from the query
    df = pd.read_sql_query(query, con)

# create a bar chart of countries with lowest mortality
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(df['country'], df['e_mort_100k'], color='deepskyblue', edgecolor='black')

ax.bar_label(bars, fmt='%.2f', padding=3, rotation=45, fontsize=9)

ax.set_ylabel('TB deaths per 100k')
ax.set_xlabel('Country')
ax.set_title('Countries with 20 lowest TB Deaths per 100k (2023)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# create a table of countries who reduced mortality rate by 50% from
with sqlite3.connect(db_name) as con:
    query = '''
    SELECT t2023.country
    FROM tbdata AS t2023
    JOIN tbdata AS t2020
      ON t2023.country = t2020.country
    WHERE t2023.year = 2023
      AND t2020.year = 2020
      AND t2023.e_mort_100k <= 0.5 * t2020.e_mort_100k
    '''

# create df from the query 
    df = pd.read_sql_query(query, con)

print(df)