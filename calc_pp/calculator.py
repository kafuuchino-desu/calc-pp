import ast
import math
import operator
from abc import ABC
from typing import Optional, Union

import simpleeval

from calc_pp.configure import Configure
from calc_pp.variables import varTypes, varsProvider

RESULT = Union[int, float, str, bool]
operators = ["+", "-", "*", "/", "(", ")"]
#sizes of chests and shulkers (in grids, W*H)
sizeChest = 9*6
sizeShulker = 9*3


class Calculator(ABC):
	def __init__(self, config: Optional[Configure]):
		self.config = config

	def calculate(self, expression: str) -> Optional[RESULT]:
		"""
		Return int or float or str or bool for the result
		Return None for ignoring input
		Raise whatever if necessary
		"""
		try:
			return self._calculate(expression)
		except Exception as e:
			return '{}: {}'.format(type(e).__name__, e)

	def _calculate(self, expression: str) -> Optional[RESULT]:
		raise NotImplementedError()


class advancedCalculator(Calculator):
	def __init__(self, config: Optional[Configure]):
		super().__init__(config)
		self.evalCalc = SimpleevalCalculator(config)
		self.vars = varsProvider()
		#putting in some secret variables, hack me ;-P
		self.vars.set("_MAX_DEPTH", varTypes.CONSTANT, config.max_depth)
		self.vars.set("_STACK_SHULKERS", varTypes.CONSTANT, config.stack_shulkers)
		self.vars.set("_STACK_BASE", varTypes.CONSTANT, 64)

	def _calculate(self, expression: str) -> Optional[RESULT]:
		'''
		advanced calculator commands:
		use ==set (variable name):value/expression to set a variable
		use ==get (variable name) to get the type and value
		use ==(expression) to calculate, use a dollar sign($) before a variable to access it, eg: 123+$abc (bash-like syntax)
		'''
		depth = 0

		#set method
		if expression.startswith("set "):
			expression = expression.replace("set ", "")
			vName = expression.split(":")[0]
			value = expression.split(":")[1]
			if "$" in value:
				self.vars.set(vName, varTypes.EXPRESSION, value)
			else:
				self.vars.set(vName, varTypes.CONSTANT, value)
			return str(vName + ": " + str(value))

		#get method
		elif expression.startswith("get "):
			expression = expression.replace("get ", "")
			vName = expression.replace("$", "")
			vType, value = self.vars.get(vName)
			return str(vName + ": " + str(value))

		#stack calculator
		elif expression.startswith("stack "):
			expression = expression.replace("stack ", "")
			result = self.solve(expression, depth)
			uselessType, stackSize = self.vars.get("_STACK_BASE")
			stackSize = int(stackSize)
			uselessType, stackShulkers = self.vars.get("_STACK_SHULKERS")
			chestCount, shulkerCount, stackCount = 0, 0, 0
			if stackShulkers == 1:
				chestCount = result//(sizeChest * sizeShulker * stackSize)
				print(chestCount)
				result -= chestCount * sizeChest * sizeShulker * stackSize
				shulkerCount = result//(sizeShulker * stackSize)
				result -= shulkerCount * sizeShulker * stackSize
				stackCount = result//stackSize
				result -= stackCount * stackSize
			else:
				chestCount = result//(sizeChest * stackSize)
				result -= chestCount * sizeChest * stackSize
				stackCount = result//stackSize
				result -= stackCount * stackSize

			#build the output string
			string = ""
			if chestCount > 0:
				string += str(chestCount) + "DC "
				if stackShulkers == 1:
					string += "shulkers "
			if shulkerCount > 0:
				string += str(shulkerCount) + "shulkers "
			if stackCount > 0:
				string += str(stackCount) + "stack "
			if result > 0:
				string += str(result) + "items"
			#adding extra info
			string += f"(stacksize:{stackSize})"
			return string

		else:
			result = self.solve(expression, depth)
			self.vars.set("", varTypes.CONSTANT, result)
			return result

	def solve(self, expression: str, depth: int):

		#aborts if max depth reached
		if depth > self.getMaxDepth():
			raise ArithmeticError("Max depth reached solving expression: " + expression)
		depth += 1

		varList = self.parseVariables(expression)

		#substitute variables
		if len(varList) != 0:
			for var in varList:
				vType, value = self.vars.get(var)
				var = "$" + var
				if vType == varTypes.CONSTANT:
					#replaces the variable with value
					expression = expression.replace(var, str(value))
				elif vType == varTypes.EXPRESSION:
					#solves the expression then replace
					expression = expression.replace(var, str(self.solve(value, depth)))

		#variables are all gone, now feed the expression into eval calculator
		return self.evalCalc._calculate(expression)



	def parseVariables(self, expression: str):
		varList = []
		flagMatching = False
		variable = ""
		if "$" in expression:
			for i in expression:
				if i == "$":
					variable = ""
					flagMatching = True
				elif (i in operators) and flagMatching:
					varList.append(variable)
					flagMatching = False
					variable = ""
				#skip spaces in expressions
				elif flagMatching and (i != " "):
					variable += i
			#append the variable if expression ends with a variable
			if variable != "":
				varList.append(variable)
		return varList

	def getMaxDepth(self):
		uselessType, depth = self.vars.get("_MAX_DEPTH")
		return depth


class SimpleevalCalculator(Calculator):
	def __init__(self, config: Optional[Configure]):
		super().__init__(config)
		
		def merge(a: dict, b: dict):
			ret = a.copy()
			ret.update(b)
			return ret

		simpleeval.MAX_POWER = self.config.max_power_length
		core = simpleeval.SimpleEval(
			operators=merge(simpleeval.DEFAULT_OPERATORS, {
				ast.BitXor: operator.xor,
				ast.BitAnd: operator.and_,
				ast.BitOr: operator.or_,
				ast.RShift: operator.rshift,
				ast.LShift: operator.lshift,
			})
		)
		for k, v in math.__dict__.items():
			if not k.startswith('_'):
				if type(v) in [int, float]:
					core.names[k] = v
				elif callable(v) and k not in self.config.function_blacklist:
					core.functions[k] = v
		core.functions.update({
			'hex': lambda x: hex(x).replace('0x', '', 1).rstrip('L').upper(),
			'bin': lambda x: bin(x).replace('0b', '', 1).rstrip('L'),
			'oct': lambda x: oct(x).replace('0o', '', 1).rstrip('L'),
			'bool': bool
		})
		self.core = core

	def _calculate(self, expression: str) -> Optional[RESULT]:
		return self.core.eval(expression)