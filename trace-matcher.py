import pandas as pd
from datetime import datetime
import sys
import os

# Get the command-line arguments
args = sys.argv

# Check if the file exists
if not (os.path.exists(args[1]) and os.path.exists(args[2])):
    if not os.path.exists(args[1]):
        print(f"File does not exist {args[1]}")
    if not os.path.exists(args[2]):
        print(f"File does not exist {args[2]}")
    sys.exit(1)

publishFile=args[1]
pubackFile=args[2]

# Define a custom date parser function
def my_date_parser(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S,%f')

def my_format_time(milliseconds):
    if milliseconds < 1000:
        return f"{milliseconds} ms"
    elif milliseconds < 60000:
        return f"{milliseconds / 1000} s"
    elif milliseconds < 3600000:
        return f"{milliseconds / 60000} min"
    else:
        return f"{milliseconds / 3600000} h"

publishes = pd.read_csv(publishFile, parse_dates=['pubTime'], date_parser=my_date_parser)
pubacks = pd.read_csv(pubackFile,parse_dates=['ackTime'], date_parser=my_date_parser)

# Add a new column with an empty timestamp value
publishes['ackLine'] = pd.NaT
publishes['ackTime'] = pd.NaT
publishes['reasonCode'] = pd.NaT
publishes['diffTime'] = pd.NaT

# Loop through each publish
for pubInd, pubRow in publishes.iterrows():
    # Do something with each row
    puback=pubacks.query(f"ackLine > {pubRow.loc['pubLine']} and clientId == '{pubRow.loc['clientId']}' and packetId == {pubRow.loc['packetId']}").head(1)
    if not puback.empty:
        publishes.loc[pubInd, 'ackLine'] = puback.iloc[0].loc['ackLine']
        publishes.loc[pubInd, 'ackTime'] = puback.iloc[0].loc['ackTime']
        publishes.loc[pubInd, 'reasonCode'] = puback.iloc[0].loc['reasonCode']
        timeDiff = puback.iloc[0].loc['ackTime'] - pubRow.loc['pubTime']
        timeDiffMs = timeDiff.total_seconds() * 1000
        publishes.loc[pubInd, 'diffTime'] = timeDiffMs
        #print(f"Publish #{pubInd} of {publishes.shape[0]} has ack on line {puback.iloc[0].loc['ackLine']} in {my_format_time(timeDiffMs)}")
else:
        print(f"Publish #{pubInd} of {publishes.shape[0]} has no ack")

# Write the DataFrame to a CSV file
publishes.to_csv('results.csv', index=False)