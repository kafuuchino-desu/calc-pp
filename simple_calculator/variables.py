from enum import Enum

numbers = [str(i) for i in range(0, 10)]

class varTypes(Enum):
	CONSTANT = 0
	EXPRESSION = 1

class varsProvider(object):
	def __init__(self):
		self.dict = {}
		self.dict[""] = []

	def set(self, key, type: varTypes, value):
		keyStr, keyIndex = self.parseKey(key)

		#special built-in history list
		if keyStr == "":
			self.dict[""].append(value)

		else:
			#creates the key if it's not in the dictionary
			if keyStr not in self.dict:
				self.dict[key] = {}

			self.dict[keyStr][keyIndex] = {"type" : type, "value" : value}

	def get(self, key):
		keyStr, keyIndex = self.parseKey(key)

		#special built-in history list
		if keyStr == "":
			#note that in default returned keyIndex is offsetted by 1
			return varTypes.CONSTANT, self.dict[""][-int(keyIndex)]

		#checks if key and index in the dictionary, if not, raise an exception
		if (keyStr in self.dict) and (keyIndex in self.dict[keyStr]):
			type = self.dict[keyStr][keyIndex]["type"]
			value = self.dict[keyStr][keyIndex]["value"]
			return type, value
		else:
			raise ValueError

	def clear(self):
		self.dict = {}
		self.dict[""] = []

	#where the magic happens
	def parseKey(self, key):
		keyString = ""
		keyIndex = ""
		for i in key:
			if i not in numbers:
				if keyIndex == "":
					keyString += i
				else:
					keyString += keyIndex
					keyString += i
					keyIndex = ""
			else:
				keyIndex += i

		if keyIndex == "":
			keyIndex = "1"
		else:
			keyIndex = str(int(keyIndex) + 1)

		return keyString, keyIndex

#TLDR: tests for dev
if __name__ == "__main__":
	vars = varsProvider()
	print(vars.parseKey("test"))
	print(vars.parseKey("test1"))
	print(vars.parseKey("test2"))
	print(vars.parseKey("test01"))
	print(vars.parseKey("test01test"))
	print(vars.parseKey("test01test1"))

	#history shennanigans
	print(vars.parseKey("1"))

	
	vars.set("test", varTypes.CONSTANT, 810)
	vars.set("test1", varTypes.EXPRESSION, "verycoolexpression")
	print(vars.get("test"))
	print(vars.dict)
	print("=============================")
	vars.set("test", varTypes.CONSTANT, 893)
	print(vars.dict)
	print("=============================")
	vars.set("test", varTypes.EXPRESSION, "OVERWRITE!")
	vars.set("test2", varTypes.EXPRESSION, "hey")
	vars.set("test01", varTypes.EXPRESSION, "gotcha")
	vars.set("test01anotherTest", varTypes.EXPRESSION, "idkWhatToWrite")
	vars.set("test01anotherTest01", varTypes.EXPRESSION, "justSth")
	print(vars.dict)
	print(vars.get("test"))
	print(vars.get("test2"))
	print("========HISTORY TEST=========")
	vars.clear()
	vars.set("", varTypes.CONSTANT, 1)
	vars.set("", varTypes.CONSTANT, 2)
	vars.set("", varTypes.CONSTANT, 3)
	vars.set("", varTypes.CONSTANT, 4)
	print(vars.get("0"))
	print(vars.get("1"))
	print(vars.dict)
	print(vars.get("gimmeException"))