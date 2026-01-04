import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# bring in url and store csv file
url = ('https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-12-16/roundabouts_clean.csv')
roundabouts = pd.read_csv(url)

db_name = 'Roundabouts.db'

# create database
def create_database(db_name):
    if not os.path.exists(db_name):
        print(f'Data base {db_name} does not exists. Creating database.')

        with sqlite3.connect(db_name) as con:
            roundabouts.to_sql('roundabouts', con, if_exists='replace', index=False)
            print(f'Database {db_name} created.')

    else:
        print('The data base already exists.')

create_database(db_name)

# create a sql query to count and print number of roundabouts in each city
def count_by_city():
    with sqlite3.connect(db_name) as con:
        # sql query
        query = '''
        SELECT 
            town_city,
            COUNT(*) AS roundabout_count
        FROM roundabouts
        WHERE town_city IS NOT NULL AND town_city <> ''
        GROUP BY town_city
        ORDER BY roundabout_count desc
        '''

        df = pd.read_sql_query(query, con)

        print(df.head(10))
        return df
    
count_by_city()

# count by country and make a bar graph for countries with roundabouts 100+
def count_by_country():
    with sqlite3.connect(db_name) as con:
        query = '''
        SELECT
            country,
            count(*) AS country_count
        FROM roundabouts
        WHERE country IS NOT NULL AND country <> ''
        GROUP BY country
        HAVING COUNT(*) > 99
        ORDER BY country_count desc
        '''

        df_country = pd.read_sql_query(query, con)
    
    # create a bar graph 
    plt.figure()
    plt.bar(df_country['country'], df_country['country_count'])

    plt.title('Countries with 100+ Roundabouts')
    plt.xlabel('Country')
    plt.ylabel('Number of Roundabouts')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.show()

count_by_country()

# count by state for US roundabouts and choropleth map. Use length 2 to remove counties and only look at states.
def state_count():
    with sqlite3.connect(db_name) as con:
        query = '''
        SELECT
            UPPER(TRIM(state_region)) AS state_region,
            COUNT(*) AS state_count
        FROM roundabouts
        WHERE country = 'United States'
          AND state_region IS NOT NULL
          AND TRIM(state_region) <> ''
          AND LENGTH(TRIM(state_region)) = 2
        GROUP BY UPPER(TRIM(state_region))
        HAVING COUNT(*) > 10
        ORDER BY state_count DESC
        '''
        df_state = pd.read_sql_query(query, con)

    # Normalize again (in case something slips through)
    df_state['state_region'] = df_state['state_region'].astype(str).str.upper().str.strip()

    # Safety check: if this prints 0 rows, that's the issue
    print('Rows to plot:', len(df_state))
    print(df_state.head(10))

    fig = px.choropleth(
        df_state,
        locations='state_region',
        locationmode='USA-states',
        color='state_count',
        scope='usa',
        hover_name='state_region',
        hover_data={'state_count': True, 'state_region': False},
        title='Roundabouts per State (States with >10)'
    )

    # These settings make filled states visually obvious
    fig.update_traces(marker_line_width=0.5)
    fig.update_layout(margin={'r': 0, 't': 60, 'l': 0, 'b': 0})

    fig.show()
    return df_state

df_state = state_count()

# list how many approaches and stat which is most common?
def approaches_count():
    with sqlite3.connect(db_name) as con: 
        query = '''
        SELECT 
            approaches,
            count(*) as total
        FROM roundabouts
        WHERE 
            approaches IS NOT NULL
            AND approaches <> ''
        Group BY approaches
        ORDER BY total desc
        '''
        df_approaches = pd.read_sql_query(query, con)
        print(df_approaches)

        print(f'The most common number of approaches for a roundabout is {df_approaches['approaches'].iloc[0]} approaches with {df_approaches['total'].iloc[0]} total roundabouts.')

approaches_count()