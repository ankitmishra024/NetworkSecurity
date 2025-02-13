import logging
import os
from datetime import datetime

## Log_file format
LOG_FILE=f"{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.log"

## log_file path where log get store
log_path=os.path.join(os.getcwd(),"logs",LOG_FILE)

# print(os.getcwd())
os.makedirs(log_path, exist_ok= True)

log_dir = os.path.join(log_path, LOG_FILE)

logging.basicConfig(
    filename=log_dir,
    format= "[%(asctime)s] %(lineno)d %(name)s -%(levelname)s -%(message)s",
    level=logging.INFO
)
