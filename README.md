# trace-parser-publish-puback
Parse HiveMQ trace recording and calculate time duration between PUBLISH and matching PUBACK events

## Prerequisits
You will need:
- `bash`
- `python3`
  - `pandas`
- `grep`
- `rg`

## Prehistory
Trace Recording is usually downloaded as a zip file, e.g. `my-trace-recording.zip`
When the archive is unzipped, trace log files for each node are located in their own subdirectory named by the HiveMQ cluster node name:
```
my-trace-recording
├── i5rUM
│   ├── my-trace-recording.1.trace
│   ├── my-trace-recording.2.trace
│   └── my-trace-recording.trace
├── vNPR5
│   └── my-trace-recording.trace
└── wheVV
├── my-trace-recording.1.trace
├── my-trace-recording.2.trace
└── my-trace-recording.trace
```

## How to run
Run the Bash script `trace-parser.sh` specifying the directory name as first argument:
```
./trace-parser.sh $HOME/Downloads/my-trace-recording
```
Results are saved to CSV file:
```
results.csv
```

## How it works
The `trace-parser.sh` script will:
- Glue all trace files from subdirectories into one file
- Sort the glued file by date
- Grep PUBLISH and PUBACK lines together with their line number
- Using `rg` for regular expression parsing, extract the data into PUBLISH- and PUBACK- CSV files

Then `trace-parser.sh` Bash script will run the Python script `trace-parser.py` specifying the PUBLISH- and PUBACK- CSV files as first and second argument.
The Python script will:
- import the CSV files into Pandas DataFrames
- match each PUBLISH to PUBACK packet
- calculate the time duration between the two packets
- save results to `results.csv` file

## Troubleshooting
If the `trace-parser.sh` cannot find the `trace-parser.py`, edit the `trace-parser.sh` and set correct absolute path to `trace-parser.py`.