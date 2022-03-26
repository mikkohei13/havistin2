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
filename = "./import/atlas3-grid-data.txt"

df = pd.read_csv(filename, sep='\t')
df = df.replace(np.nan, '', regex=True)

print("Finished loading into dataframe")

df.sort_values(by=['N','E'], inplace=True)

print("Sorted dataframe")

# TODO: use dataframe instead to handle and export the data?
data = df.to_dict(orient='records')

print("Finished loading into dict")


# Name data

filename_names = "./import/species-names.txt"

nameframe = pd.read_csv(filename_names, sep='\t')
nameframe = nameframe.replace(np.nan, '', regex=True)

names = nameframe.set_index('speciesAbbr').to_dict(orient='index')

#print(names) # debug


gridCodeMem = ""
#gridSpeciesList = []
gridSpeciesDict = dict()

for i, row in enumerate(data):

    thisGridCode = str(row["N"]) + ":" + str(row["E"])
#    thisGridSpeciesDict = dict()

    # New grid starts
    if thisGridCode != gridCodeMem:

#        save_file(gridCodeMem, gridSpeciesList)
        save_file(gridCodeMem, gridSpeciesDict)
        gridCodeMem = thisGridCode
#        gridSpeciesList = []
        gridSpeciesDict = dict()

    # Remove unnecessary rows
    row.pop("N", None)
    row.pop("E", None)
    row.pop("speciesCode", None)

    # Add Finnish name

    # List abbreviations that are missing from name field
#    if not row["speciesAbbr"] in names:
#        print(row["speciesAbbr"])
#        continue

    # Skip species that don't have Finnish name in the species list
    if names[row["speciesAbbr"]]["speciesFI"]:
        row["speciesFi"] = names[row["speciesAbbr"]]["speciesFI"].lower()
    else:
        continue

#    gridSpeciesList.append(row)
    gridSpeciesDict[row["speciesFi"]] = row


    step = 1000
    if i % step == 0:
        print("Done " + str(i) + " rows")

    if i >= debugLimit:
        print("Debug limit " + str(debugLimit))
        break


