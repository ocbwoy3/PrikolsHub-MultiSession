"""
# Script
Implementation of scripts in MultiSession PrikolsHub RoControl.
"""

Script_Emojis = {
    "NORMAL": ["Script","<:script:1150375864937226240>"],
	"PRIKOLSHUB": ["Official","<:Prikols_V2:1130242240636276846>"],
	"RARE": ["Rare","<:fire_instance:1150375860898123827>"],
	"UNLEAKED": ["Unleaked","<:canvasgroup:1150377188458254387>"],
	"UTILITY": ["Utility","<:configuration:1150375856724779099>"],
	"HUB": ["Hub","<:screengui:1150375862361935942>"],
	"ABUSIVE": ["Abusive","<:clickdetector:1150375855625863238>"],
	"SKIDDED": ["Skidded","<:explosion:1150375858071162911>"],
	"CR": ["CR","<:remote_event:1150373797128568853>"],
	"FURRY": ["Furry","🐾"]
}

class ScriptTypes:
	NORMAL = "NORMAL"
	PRIKOLSHUB = "PRIKOLSHUB"
	RARE = "RARE"
	UNLEAKED = "UNLEAKED"
	UTILITY = "UTILITY"
	HUB = "HUB"
	ABUSIVE = "ABUSIVE"
	SKIDDED = "SKIDDED"
	CR = "CR",
	FURRY = "FURRY"

class Script:
	name:str = None
	author:str = None
	script:str = None
	script_type:str = None
	__customEmoji__:str = None
	submitted = None
	def __init__(self,script:str,name:str,author:str,script_type:str,customEmoji:str=None,submitted:bool=False):
		self.script = script
		self.name = name
		self.author = author
		self.script_type = script_type
		self.__customEmoji__ = customEmoji
		self.submitted = submitted
	
	def getEmoji(self):
		x = None
		if Script_Emojis[self.script_type]:
			x = Script_Emojis[self.script_type]
		else:
			x = Script_Emojis[ScriptTypes.NORMAL]

		if self.__customEmoji__:
			return [x[0],self.__customEmoji__]
		else:
			return x