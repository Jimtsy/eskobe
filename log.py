import logging
import sys
import os
import logging.config
import simplejson as json
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger

_log_dir = os.environ.get('LOG_DIR', os.path.curdir)
_log_name = os.environ.get("LOG_NAME", "eskobe.log")
_level = os.environ.get("LEVEL", logging.INFO)

if _log_dir and os.path.isdir(_log_dir):
    LOG_FILE = os.path.join(_log_dir, _log_name)
else:
    LOG_FILE = _log_name

if _level not in (logging.INFO, logging.DEBUG, logging.ERROR, logging.WARNING):
    _level = logging.INFO

LOGGING_LEVEL = _level


def log_enable():
    try:
        bak_time = datetime.now().__format__("%m-%d")
        os.rename(_log_dir + "/" + _log_name, "{}/eskobe-{}.log".format(_log_dir, bak_time))
    except FileNotFoundError:
        pass

    fmt = '"%(asctime)s - %(threadName)s - %(levelname)s - %(message)s - %(lineno)s - %(filename)s"'
    json_formatter = jsonlogger.JsonFormatter(fmt, json_encoder=json.JSONEncoder)

    log = logging.getLogger(__name__)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(LOGGING_LEVEL)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(LOGGING_LEVEL)

    logging.config.dictConfig({"disable_existing_loggers": False, "version": 1})
    logging.root.handlers = [console_handler, file_handler]
    logging.root.setLevel(LOGGING_LEVEL)
    logging.getLogger("requests").setLevel(LOGGING_LEVEL)

    return log

logger = log_enable()
logger.info("_log_dir={}, _log_name={}, _level={}".format(_log_dir, _log_name, _level))

