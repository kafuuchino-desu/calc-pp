from typing import List

from mcdreforged.api.utils import Serializable


class Configure(Serializable):
	max_result_length = 1000  # maximum result string length
	max_power_length = 10000  # simpleeval.MAX_POWER override
	max_depth = 16 # maximum calls for a single expression object
	function_blacklist: List[str] = [
		'exp', 'expm1', 'ldexp', 'pow', 'factorial'
	]
