# data on Flint water lead concentration

import pandas as pd
import os
import sqlite3
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

# # create variable for base url
# url ='https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2025/2025-11-11/diabetes.csv'

# # create df for data
# diabetes = pd.read_csv(url)

# # create database and import files
# db_name = "IndianDiabetes.db"

# def create_sql(db_name):
#     if not os.path.exists(db_name):
#         print(f'Database not found, creating {db_name}. 🤓')
#         with sqlite3.connect (db_name) as con:
#             diabetes.to_sql('diabetes', con, if_exists='replace', index=False)
#             print(f"Database {db_name} created with table 'diabetes'. 👍")
#     else:
#         print('Database already exists. 🧮')

# create_sql(db_name)

# create function to test significant difference of diabtetes status and secondary column
def test_of_sig(db_path, factor):
    with sqlite3.connect(db_path) as con:
        # Query data (only pull needed columns)
        query = f"""
            SELECT diabetes_5y, {factor}
            FROM diabetes
            WHERE {factor} IS NOT NULL
        """
        df = pd.read_sql_query(query, con)

    # Split into positive and negative groups
    pos_group = df[df['diabetes_5y'] == 'pos'][factor].dropna()
    neg_group = df[df['diabetes_5y'] == 'neg'][factor].dropna()

    # Run t-test
    t_stat, p_val = stats.ttest_ind(pos_group, neg_group, equal_var=False)

    # Interpret results
    result = 'Significant difference' if p_val < 0.05 else 'No significant difference'

    # Print results
    print(f'Factor tested: {factor}')
    print(f'Mean (pos): {pos_group.mean():.2f}, Mean (neg): {neg_group.mean():.2f}')
    print(f't = {t_stat:.3f}, p = {p_val:.3f} ➡️  {result}')
    print('')

    # Return output to be used later if desired
    return {
        'factor': factor,
        'mean_pos': pos_group.mean(),
        'mean_neg': neg_group.mean(),
        't_stat': t_stat,
        'p_value': p_val,
        'result': result
    }

test_of_sig('IndianDiabetes.db', 'age')
test_of_sig('IndianDiabetes.db', 'pregnancy_num')
test_of_sig('IndianDiabetes.db', 'triceps_mm')
test_of_sig('IndianDiabetes.db', 'bmi')

# graph of the mean per group
def graph_aves(db_path, factor):
    with sqlite3.connect(db_path) as con:
        # Query data (only pull needed columns)
        query = f"""
            SELECT diabetes_5y, {factor}
            FROM diabetes
            WHERE {factor} IS NOT NULL
        """
        df = pd.read_sql_query(query, con)

    # Split into positive and negative groups
    pos_group = df[df['diabetes_5y'] == 'pos'][factor].dropna()
    neg_group = df[df['diabetes_5y'] == 'neg'][factor].dropna()

# Compute stats
    mean_pos, mean_neg = pos_group.mean(), neg_group.mean()
    median_pos, median_neg = pos_group.median(), neg_group.median()

    # Data structure for plotting
    labels = ['Mean', 'Median']
    pos_values = [mean_pos, median_pos]
    neg_values = [mean_neg, median_neg]

    # Plot setup
    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(7, 5))
    plt.bar(x - width/2, pos_values, width=width, color='red', label='Positive')
    plt.bar(x + width/2, neg_values, width=width, color='blue', label='Negative')

    # Labels & formatting
    plt.xticks(x, labels)
    plt.ylabel(factor)
    plt.title(f'{factor.capitalize()} — Mean and Median by Diabetes Status')
    plt.legend()
    plt.tight_layout()
    plt.show()

    return pd.DataFrame({
        'Statistic': ['Mean', 'Median'],
        'Positive': pos_values,
        'Negative': neg_values
    })

graph_aves('IndianDiabetes.db', 'age')
graph_aves('IndianDiabetes.db', 'pregnancy_num')
graph_aves('IndianDiabetes.db', 'triceps_mm')
graph_aves('IndianDiabetes.db', 'bmi')