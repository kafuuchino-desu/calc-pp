from mcdreforged.api.all import *

from calc_pp.calculator import advancedCalculator
from calc_pp.configure import Configure

config = Configure.get_default()

def calc(expression: str):
	if not expression:
		return None
	result = calculator.calculate(expression)
	if result is None:
		return None
	elif isinstance(result, float):
		result = round(result, 12)  # makes sin(pi) look nicer
	elif isinstance(result, str):
		return result
	else:
		result = str(result)
		if len(result) > config.max_result_length:
			result = result[:max(config.max_result_length - 3, 0)] + '...'
	return result


def on_user_info(server: PluginServerInterface, info: Info):
	if info.content.startswith('=='):
		expression = info.content[2:]
		result = calc(expression)
		if result:
			info.cancel_send_to_server()
			if info.is_from_console:
				server.logger.info(result)
			else:
				server.say(
					RTextList(RText('==', RColor.gray), result).
					h(RTextList(
						RText.format('{}  {}  {}\n', expression, RText('->', RColor.gray), result),
						RText('--------\n', RColor.dark_gray),
						server.rtr('simple_calculator.result_hover')
					)).
					c(RAction.suggest_command, result)
				)


def on_load(server: PluginServerInterface, old):
	global config, calculator
	config = server.load_config_simple(target_class=Configure)
	calculator = advancedCalculator(config)
	server.logger.info('Used {} for calculation'.format(calculator.__class__.__name__))
	server.register_help_message('==<expression>', server.rtr('simple_calculator.help'))


def main():
	while True:
		print(calc(input()))


if __name__ == '__main__':
	main()
