# Pydy Tuesday age gaps in hollywood
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt

# Load the dataset directly from GitHub (same link as in the R code)
url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2023/2023-02-14/age_gaps.csv"

# save data in a dataframe named age_gaps
age_gaps = pd.read_csv(url)

# name database
db_name = 'age_differences.db'

# create database
if not os.path.exists(db_name):
    print(f'Database not found, creating {db_name}. 🤓')
    
    # Create/connect DB and save create data tables
    with sqlite3.connect(db_name) as con:
        age_gaps.to_sql('age_gaps', con, if_exists='replace', index=False)
        print(f"Database {db_name} created with table 'age_gaps'. 👍")
else:
    print('Database already exists. 🧮')

# query to filter where character 1 is a woman
with sqlite3.connect(db_name) as con:
    query = """
        SELECT movie_name, (actor_1_age - actor_2_age) AS age_gap
        FROM age_gaps
        WHERE character_1_gender = 'woman'
          AND (actor_1_age - actor_2_age) > 5;
    """
    df = pd.read_sql_query(query, con)

# Step 4: Plot bar chart
plt.figure(figsize=(12, 6))
plt.bar(df["movie_name"], df["age_gap"])
plt.xticks(rotation=90)
plt.xlabel("Movie")
plt.ylabel("Age Gap")
plt.title("Age gaps > 5 years where the main character is a woman")
plt.tight_layout()
plt.show()