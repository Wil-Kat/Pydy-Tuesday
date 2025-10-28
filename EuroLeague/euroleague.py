# Pydy Tuesday EuroLeague Basketball

import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt

# load the dataset from github
url = 'https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-10-07/euroleague_basketball.csv'

# save data to a dataframe
euroleague = pd.read_csv(url)

# name database
db_name = 'EuroLeague.db'

# create database
if not os.path.exists(db_name):
    print(f'Database not found. Creating {db_name}. 🤓')
    # connect and create
    with sqlite3.connect(db_name) as con:
        euroleague.to_sql('basketball', con, if_exists='replace', index=False)
        print(f"Database {db_name} created with table 'basketball'. 👍")
else:
    print('Database already exists. 🧮')

# query organizing arenas by capacity
with sqlite3.connect(db_name) as con:
    query = '''
        SELECT Arena, Capacity, Country
        FROM basketball
        ORDER BY Capacity
    '''
    df = pd.read_sql_query(query, con)

# print the results to the terminal
print("\nArenas Organized by Capacity:\n")
print(df.to_string(index=False))

with sqlite3.connect(db_name) as con:
    query = '''
        SELECT Country, Capacity
        FROM basketball
    '''
    df = pd.read_sql_query(query, con)

# clean the Capacity column to keep only the first number
df['Capacity'] = (
    df['Capacity']
    .astype(str)                             # ensure all values are strings
    .str.extract(r'(\d[\d,]*)')[0]           # extract the first numeric group
    .str.replace(',', '', regex=False)       # remove commas
    .astype(float)                           # convert to numeric
)

# group by country and sum capacities (some countries have multiple arenas)
country_capacity = df.groupby('Country', as_index=False)['Capacity'].sum()

# sort by capacity (descending)
country_capacity = country_capacity.sort_values(by='Capacity', ascending=False)

# print results to terminal
print("\n🏀 Total Seating Capacity by Country:\n")
print(country_capacity.to_string(index=False))

# plot bar chart
plt.figure(figsize=(10, 6))
plt.bar(country_capacity['Country'], country_capacity['Capacity'])
plt.ylabel('Total Seating Capacity')
plt.xlabel('Country')
plt.title('EuroLeague Arena Seating Capacity by Country')
plt.xticks(rotation=45, ha='right')  # rotate country labels for readability
plt.tight_layout()
plt.show()