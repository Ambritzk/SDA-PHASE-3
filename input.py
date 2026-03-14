from multiprocessing import Queue
from typing import Dict, List, Any
import pandas as pd
import csv

def RenameColumn(config: Dict, original_column_name: str,original_value: Any, columns: List[Dict]) -> str:
    for column in columns:
        if column.get('source_name') == original_column_name:
            required_data_type = column.get('data_type')
            if required_data_type == "string":
                casted_value = str(original_value)
            elif required_data_type == "integer":
                casted_value = int(original_value)
            elif required_data_type == "float":
                casted_value = float(original_value)

            return column.get('internal_mapping'), casted_value
    
    #else column not found. Handle exception here?
def run(config: Dict, InputQueue: Queue) -> None:
    try:
        with open(config.get('dataset_path'), 'r') as DataFile:
            csv_reader = csv.DictReader(DataFile)
            columns: List[Dict] = config["schema_mapping"].get('columns')
        
            renaming = lambda x: {RenameColumn(config,k,v,columns)[0]:RenameColumn(config,k,v,columns)[1] for k,v in x.items()}
            ListOfDicts = list(map(renaming, csv_reader))
    except FileNotFoundError:
        print('File not found!')
    print(pd.DataFrame(ListOfDicts))


