dt_fmt = '%Y-%m-%d %H:%M:%S'
dt_fmt_o = '%Y-%m-%d %H:%M:%S'

import logging, time

formatter = logging.Formatter('\u001b[1;30m{asctime}\u001b[0m \u001b[1;34m{levelname:<8}\u001b[0m \u001b[0;35m{name}\u001b[0m {message}', dt_fmt, style='{')

class CustomLogger:
	name = "logger"
	
	def __init__(self,name:str):
		self.name = name

	def log(self,message:str,levelname:str):
		asctime = time.strftime(dt_fmt)
		print(f'\u001b[1;30m{asctime}\u001b[0m \u001b[1;34m{levelname:<8}\u001b[0m \u001b[0;35m{self.name}\u001b[0m {message}')

	def debug(self,msg:str):
		self.log(msg,"DEBUG")
	
	def info(self,msg:str):
		self.log(msg,"INFO")
	
	def warn(self,msg:str):
		self.log(msg,"WARN")
	
	def error(self,msg:str):
		self.log(msg,"ERROR")
	
	def critical(self,msg:str):
		self.log(msg,"CRITICAL")

def getLogger(logger_name:str):
	logger = logging.getLogger(logger_name)
	if 'discord' in logger_name:
		return logger
	logger.setLevel(logging.DEBUG)
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logger.handlers = [handler]
	return logger

prikols_logger = CustomLogger("prikolshub")
splogger = CustomLogger("prikolshub.session_pool")