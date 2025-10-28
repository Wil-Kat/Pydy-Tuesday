# imports
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from pathlib import Path

# database URL
url = 'https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2024/2024-05-07/rolling_stone.csv'

# read in csv files
album_ranks = pd.read_csv(url)

# create the database
db_path = Path('RollingStone.db')
if not db_path.exists():
    print(f'Data base {db_path} not found, created the database. 📊')

    # connect to database and create the data table
    with sqlite3.connect(db_path) as con:
        album_ranks.to_sql('album_ranks', con, if_exists='replace', index=False)
        print('Data table album_ranks has been created. 🧮')

else:
    print('Database already exists. 🤓')

# create a function to read store all albums who charted for 100+ weeks
def over_100_weeks():
    with sqlite3.connect(db_path) as con:
        query = '''
        SELECT album, weeks_on_billboard AS charts
        FROM album_ranks
        WHERE weeks_on_billboard > 99
        '''
        df = pd.read_sql_query(query, con)

    # create bar chart of album names and weeks on top of charts
    plt.figure(figsize=(15, 8))
    plt.bar(df['album'], df['charts'])
    plt.xticks(rotation=90)
    plt.xlabel('Album Name')
    plt.ylabel('Weeks')
    plt.title('Albums on billboard chart for 100+ weeks')
    plt.tight_layout()
    plt.show()

# create function to see artist who declined in ranks more than 250 positions
def largest_decline():
    with sqlite3.connect(db_path) as con:
        query = '''
        SELECT clean_name, differential
        FROM album_ranks
        WHERE differential < -249 AND rank_2020 IS NOT NULL
        '''
    df = pd.read_sql_query(query, con)

    # create bar chart 
    plt.figure(figsize=(10, 6))
    plt.bar(df['clean_name'], df['differential'])
    plt.xticks(rotation=90)
    plt.xlabel('Artist')
    plt.ylabel('Positions Dropped')
    plt.title('Artist who dropped 250+ positions in rank')
    plt.tight_layout()
    plt.show()

def release_rank():
    with sqlite3.connect(db_path) as con:
        query = '''
        SELECT rank_2020, release_year
        FROM album_ranks
        WHERE rank_2020 < 51
        '''
    df = pd.read_sql_query(query, con)

    # create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(df['release_year'], df['rank_2020'], alpha=0.7)
    plt.xlabel("Year of Release")
    plt.ylabel("Ranking")
    plt.title("Album Rankings by Year of Release")

    # invert y-axis because position 1 is best
    plt.gca().invert_yaxis()
    plt.show()

# create a pie chart of release decade of ranked albums in 2020
def album_decades():
    with sqlite3.connect(db_path) as con:
        query = '''
        SELECT release_year
        FROM album_ranks
        WHERE rank_2020 IS NOT NULL
        '''

    # group by decade of release
    df = pd.read_sql_query(query, con)
    df['decade'] = (df['release_year'] // 10) * 10
    decade_counts = df['decade'].value_counts().sort_index()

       # Plot pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(decade_counts, labels=decade_counts.index,
            autopct='%1.1f%%', startangle=140)
    plt.title('Percentage by Decade of Ranked Albums')
    plt.show()

over_100_weeks()
largest_decline()
release_rank()
album_decades() 