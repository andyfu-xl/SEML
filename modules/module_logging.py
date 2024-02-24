import logging

module_dict = {
    'MAIN': './logs/main.log',
    'COMMUNICATOR': './logs/communicator.log',
    'DATABASE': './logs/database.log',
    'DATAPARSER': './logs/dataparser.log',
    'PREPROCESSOR': './logs/preprocessor.log',
    'MESSAGETYPES': './logs/messagetypes.log'
}

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