import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from pathlib import Path
import numpy as np

# URLs to the datasets
base_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2025/2025-02-04/"

# Read each CSV into a pandas DataFrame
simpsons_characters = pd.read_csv(base_url + "simpsons_characters.csv")
simpsons_episodes = pd.read_csv(base_url + "simpsons_episodes.csv")
simpsons_locations = pd.read_csv(base_url + "simpsons_locations.csv")
simpsons_script_lines = pd.read_csv(base_url + "simpsons_script_lines.csv")

# create database for simpsons data
db_path = Path('simpsons.db')
if not db_path.exists():
    print('Database not found, creating simpsons.db. 🤓')

    # Create/connect DB and save create data talbles
    with sqlite3.connect(db_path) as con:
        con.execute("PRAGMA foreign_keys = ON;")

        simpsons_characters.to_sql("simpsons_characters", con, if_exists="replace", index=False)
        simpsons_episodes.to_sql("simpsons_episodes", con, if_exists="replace", index=False)
        simpsons_locations.to_sql("simpsons_locations", con, if_exists="replace", index=False)
        simpsons_script_lines.to_sql("simpsons_script_lines", con, if_exists="replace", index=False)

    print(f"simpsons.db created at {db_path.resolve()} ✅")

else:
    print(f"Database already exists at {db_path.resolve()} 🪇.")

# Query: count speaking lines by season for the given character
db_path = "simpsons.db"

# Character IDs
characters = {
    "Marge": 1,
    "Homer": 2,
    "Lisa": 9,
    "Bart": 8,
    "Maggie": 105,
}

# Build the SQL with an IN (...) list for the characters
placeholders = ",".join(["?"] * len(characters))
sql = f"""
SELECT
  e.season AS season,
  s.character_id,
  COUNT(*) AS speaking_lines
FROM simpsons_script_lines s
JOIN simpsons_episodes e
  ON s.episode_id = e.id
WHERE
  s.character_id IN ({placeholders})
  AND CASE
        WHEN s.speaking_line IS NULL THEN 0
        WHEN LOWER(CAST(s.speaking_line AS TEXT)) IN ('false','0','no','n','f') THEN 0
        ELSE 1
      END = 1
GROUP BY e.season, s.character_id
ORDER BY e.season, s.character_id;
"""

with sqlite3.connect(db_path) as con:
    df_long = pd.read_sql_query(sql, con, params=list(characters.values()))

# Pivot: rows = season, columns = character name, values = speaking_lines
id_to_name = {v: k for k, v in characters.items()}
df_long["character"] = df_long["character_id"].map(id_to_name)

df = (
    df_long
    .pivot_table(index="season", columns="character", values="speaking_lines", aggfunc="sum", fill_value=0)
    .sort_index()
)

# Ensure all seasons 1..28 appear even if zeros
all_seasons = pd.Index(range(21, 27), name="season")
df = df.reindex(all_seasons, fill_value=0)

print(df.head(10))  # peek

# ---- Plot: grouped bar by season ----
fig, ax = plt.subplots()  # (use subplots to avoid plt.figure issues)
n_chars = df.shape[1]
x = np.arange(len(df.index))  # seasons positions
width = 0.8 / n_chars         # total width split among characters

for i, col in enumerate(df.columns):
    ax.bar(x + i*width - (width*(n_chars-1)/2), df[col].values, width, label=col)

ax.set_xlabel("Season")
ax.set_ylabel("Number of speaking lines")
ax.set_title("Speaking lines by season")
ax.set_xticks(x)
ax.set_xticklabels(df.index)
ax.legend(title="Character")
plt.tight_layout()
plt.show()