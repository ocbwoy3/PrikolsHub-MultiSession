dt_fmt = '%Y-%m-%d %H:%M:%S'

import logging

formatter = logging.Formatter('\u001b[1;30m{asctime}\u001b[0m \u001b[1;34m{levelname:<8}\u001b[0m \u001b[0;35m{name}\u001b[0m {message}', dt_fmt, style='{')

def getLogger(logger_name:str):
	logger = logging.getLogger(logger_name)
	if 'discord' in logger_name:
		return logger_name
	logger.setLevel(logging.DEBUG)
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	return logger
