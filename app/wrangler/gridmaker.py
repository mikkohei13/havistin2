import pandas as pd
import numpy as np
import json 
import sys

'''
Converts Atlas 3 result tsv-file into grid square -specific json-files.
'''

# Save as json
def save_file(gridCode, data):
    filename = "./export/" + gridCode.replace(":", "-") + ".json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    return True


debugLimit = 1000000

# Source data
filename = "./atlas3-grid-data.txt"

# Replace NaN values with empty string 
df = pd.read_csv(filename, sep='\t')
df = df.replace(np.nan, '', regex=True)

print("Finished loading into dataframe")

df.sort_values(by=['N','E'], inplace=True)

print("Sorted dataframe")

# TODO: use dataframe instead to handle and export the data?
data = df.to_dict(orient='records')

print("Finished loading into dict")

gridCodeMem = ""
gridSpeciesList = []

for i, row in enumerate(data): 

    thisGridCode = str(row["N"]) + ":" + str(row["E"])

    # New grid starts
    if thisGridCode != gridCodeMem:

        save_file(gridCodeMem, gridSpeciesList)
        gridCodeMem = thisGridCode
        gridSpeciesList = []

    # Remove unnecessary rows
    row.pop("N", None)
    row.pop("E", None)
    row.pop("speciesCode", None)

    gridSpeciesList.append(row)

    step = 100
    if i % step == 0:
        print("Done " + str(i) + " rows")

    if i >= debugLimit:
        print("Debug limit " + str(debugLimit))
        break


