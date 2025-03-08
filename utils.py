import logging
import logging.config
logging.config.fileConfig('loggers.conf')

def generate_logger(logger_config = "basicLogger"):
  return logging.getLogger(logger_config)

  # import logging
  # return logging