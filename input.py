from multiprocessing import Queue
from typing import Dict, List, Any, Tuple
import time
import csv


def MapToInternal(config: Dict, original_column_name: str,original_value: Any, columnsFromConfig: List[Dict]) -> Tuple[str,Any]:
    
    #in config.json/schema_mapping there exists a list of dictionaries called columns
    #The line below filters those dictionaries to get the one that we need to map our current column
    #to the internal one specified in config.json
    column = next(filter(lambda x: x.get('source_name') == original_column_name, columnsFromConfig))

    required_data_type = column.get('data_type')
    if required_data_type == "string":
        casted_value = str(original_value)
    elif required_data_type == "integer":
        casted_value = int(original_value)
    elif required_data_type == "float":
        casted_value = float(original_value)

    #Here we return the internal column name and the typecasted value
    return column.get('internal_mapping'), casted_value

    #Might have to add exception handling in this function.






def run(config: Dict, InputQueue: Queue) -> None:
    try:
        with open(config.get('dataset_path'), 'r') as DataFile:
            csv_reader = csv.DictReader(DataFile)
            columnsFromConfig: List[Dict] = config["schema_mapping"].get('columns')
        
            #MapToInternal returns a set(Renamed column, value with type that matches )
            rename = lambda x: {MapToInternal(config,k,v,columnsFromConfig)[0]:MapToInternal(config,k,v,columnsFromConfig)[1] for k,v in x.items()}


            sleep_time = config['pipeline_dynamics'].get('input_delay_seconds')
            for row in csv_reader:
                packet: Dict = rename(row)
                InputQueue.put(packet)
                time.sleep(sleep_time)
            






    except FileNotFoundError:
        print('File not found!')
    except csv.Error:
        print("Something went wrong while reading data")
