import logging
from logging import handlers, getLogger

# logging.basicConfig (format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
#                     level=logging.INFO,
#                     # level=logging.DEBUG,  # Можно заменить на другой уровень логгирования.
#                     #filename = 'log/service_bot.log',
#                     )

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

_log_filename = 'log/service_bot.log'

def get_file_handler():
    #file_handler = logging.FileHandler(LOG_FILENAME)
    file_handler = handlers.RotatingFileHandler(
        _log_filename, maxBytes=52428800, backupCount=2)
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger

logging = get_logger(None)
