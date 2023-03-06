import ast
import math
import operator
from abc import ABC
from typing import Optional, Union

import simpleeval

from simple_calculator.configure import Configure
from simple_calculator.variables import varTypes, varsProvider

RESULT = Union[int, float, str, bool]
operators = ["+", "-", "*", "/", "(", ")"]


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
		#putting the max depth in secret variable, hack me ;-P
		self.vars.set("_MAX_DEPTH", varTypes.CONSTANT, config.max_depth)

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
			return str(vName + ": " + value)

		elif expression.startswith("get "):
			expression = expression.replace("get ", "")
			vName = expression
			vType, value = self.vars.get(vName)
			return str(vName + ": " + value)
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

if __name__ == '__main__':
	a = advancedCalculator(Configure)
	print(a.parseVariables("$test+123-456+$test01-$asdf"))
	print(a.parseVariables("sin($test)"))
	print(a.calculate("123 + 321"))
	print(a.calculate("pi"))
	a.vars.set("test", varTypes.CONSTANT, 114)
	print(a.vars.get("test"))
	print(a.calculate("$test+514"))