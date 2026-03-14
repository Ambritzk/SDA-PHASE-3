from multiprocessing import Queue
from typing import Dict, List
import csv

def RenameColumn(config: Dict, original_column_name: str) -> str:
    columns: List[Dict] = config.get('columns')
    for column in columns:
        if original_column_name in column.keys():
            return column.get(original_column_name)
    
    #else column not found. Handle exception here?
def run(config: Dict, InputQueue: Queue) -> None:
    try:
        with open(config.get('dataset_path'), 'r') as DataFile:
            csv_reader = csv.DictReader(DataFile)
            

            renaming = lambda x: {config.get():v for k,v in x.items()}
            ListOfDicts = [row for row in csv_reader]
    except FileNotFoundError:
        print('File not found!')


