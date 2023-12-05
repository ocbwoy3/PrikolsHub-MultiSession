class Event(object):
 
	def __init__(self):
		self.__eventhandlers = []
 
	def __iadd__(self, handler):
		self.__eventhandlers.append(handler)
		return self
 
	def __isub__(self, handler):
		self.__eventhandlers.remove(handler)
		return self
 
	def Trigger(self, *args, **keywargs):
		for eventhandler in self.__eventhandlers:
			try:
				eventhandler(*args, **keywargs)
			except:
				pass

	def Subscribe(self,handler):
		self.__eventhandlers.append(handler)