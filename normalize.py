import os
import json
import pandas as pd
import numpy as np 

import click

OUTPUT_DIR = "output"

@click.group()
def cli():
    pass

@click.command()
@click.argument('datapath', type=str)
@click.argument('setname', type=str)
def to_csv(datapath, setname):
    if not os.path.isdir(datapath):
        raise Exception('No data found')
    set_path = os.path.join(datapath, setname)
    if not os.path.isdir(set_path):
        raise Exception('Set {} not found', setname)
    files = os.listdir(set_path)
    if not files:
        raise Exception('No data found in set {}', setname)
    files.sort(reverse=True)

    first = True

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    output_file = os.path.join(OUTPUT_DIR, setname) + ".csv"

    # Get superset of columns
    print("# Reading metadata")
    columns = set();
    for i in range(len(files)):
        last_file = os.path.join(set_path, files[i])
        print("Reading metadata of file {} {}/{}".format(last_file, i+1, len(files)))
        with open(last_file, 'r') as f:
            for line in f:
                line = line.strip('\n')
                if line == "":
                    continue
                row_json = json.loads(line);
                row_df = pd.json_normalize(row_json, "items")
                columns = columns.union(set(row_df.columns.values))
    columns = list(columns)


    # Write data
    print("# Reading/Writing data")
    for i in range(len(files)):
        last_file = os.path.join(set_path, files[i])
        print("Reading/Writing data of file {} {}/{}".format(last_file, i+1, len(files)))
        with open(last_file, 'r') as f:
            for line in f:
                line = line.strip('\n')
                if line == "":
                    continue
                row_json = json.loads(line);
                row_df = pd.json_normalize(row_json, "items")
                row_df = row_df.reindex(columns=columns)
                row_df.to_csv(output_file, mode='a', header=first, columns=columns, index=False)
                first = False
    print("Wrote output to {}".format(output_file))

cli.add_command(to_csv)

if __name__ == '__main__':
    cli()