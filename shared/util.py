import os
import logging
from os import path
from datetime import datetime


def get_logger():
    if not path.exists("logs"):
        os.mkdir("logs")
        
    if not path.exists("results"):
        os.mkdir("results")
        
    log_file = "logs/logs_" + datetime.now().strftime("%m-%d-%Y__%H-%M-%S") + ".txt"
    
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    
    #Setup File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    #Setup Stream Handler (i.e. console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.DEBUG)
    
    #Get our logger
    app_log = logging.getLogger('root')
    app_log.setLevel(logging.DEBUG)
    
    #Add both Handlers
    app_log.addHandler(file_handler)
    app_log.addHandler(stream_handler)
    
    return app_log