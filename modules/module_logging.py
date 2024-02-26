import logging
import os

LOG_PATH = '/state'

module_dict = {
    'MAIN': 'main.log',
    'COMMUNICATOR': 'communicator.log',
    'DATABASE': 'database.log',
    'DATAPARSER': 'dataparser.log',
    'PREPROCESSOR': 'preprocessor.log',
    'MESSAGETYPES': 'messagetypes.log'
}

def set_log_path(log_path):
    LOG_PATH = log_path
    for key in module_dict:
        module_dict[key] = f'{LOG_PATH}/{module_dict[key]}'
        # check if the log file exists, if not create it
        if not os.path.exists(module_dict[key]):
            print(f"{module_dict[key]} does not exist. Creating it...")
            # Open the file in append mode to create it if it doesn't exist
            with open(module_dict[key], 'a') as file:
                pass  # 'pass' is just a placeholder since we don't need to write anything
        else:
            print(f"{module_dict[key]} already exists.")

def get_custom_logger(log_name, log_file, log_level):
    handler = logging.FileHandler(log_file)
    format = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
    handler.setFormatter(format)
    custom_logger = logging.getLogger(log_name)
    custom_logger.setLevel(log_level)
    custom_logger.addHandler(handler)
    return custom_logger

def main_logger(log_level, message):
    main_logger = get_custom_logger('main_log', module_dict['MAIN'], log_level)
    log_message(main_logger, log_level, message)

def communicatior_logger(log_level, message):
    communicator_logger = get_custom_logger('communicator_log', module_dict['COMMUNICATOR'], log_level)
    log_message(communicator_logger, log_level, message)

def database_logger(log_level, message):
    database_logger = get_custom_logger('database_log', module_dict['DATABASE'], log_level)
    log_message(database_logger, log_level, message)

def dataparser_logger(log_level, message):
    dataparser_logger = get_custom_logger('dataparser_log', module_dict['DATAPARSER'], log_level)
    log_message(dataparser_logger, log_level, message)

def preprocessor_logger(log_level, message):
    preprocessor_logger = get_custom_logger('preprocessor_log', module_dict['PREPROCESSOR'], log_level)
    log_message(preprocessor_logger, log_level, message)
    return None

def messagetypes_logger(log_level, message):
    messagetypes_logger = get_custom_logger('messagetypes_log', module_dict['MESSAGETYPES'], log_level)
    log_message(messagetypes_logger, log_level, message)
    return None

def log_message(logger, log_level, message):
    if log_level == 'DEBUG':
        logger.debug(message)
    elif log_level == 'INFO':
        logger.info(message)
    elif log_level == 'WARNING':
        logger.warning(message)
    elif log_level == 'ERROR':
        logger.error(message)
    else:
        logger.critical(message)
    return None