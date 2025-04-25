def pickInteger(min_choice, max_choice, message='Pick an option: '):
	try:
		choice = int(input(message))
		if choice < min_choice or choice > max_choice:
			new_message = f'Enter an integer between {min_choice} and {max_choice}: '
			choice = pickInteger(min_choice, max_choice, message=new_messsage)
		return choice
	except ValueError:
		new_message = 'Enter an integer: '
		choice = pickInteger(min_choice, max_choice, message=new_message)
		return choice

def spacePadString(string, space_padding):
	string_lines = string.splitlines(True)
	padding = ' ' *  space_padding
	new_string = ''
	for line in string_lines:
			new_string += padding + line
	return new_string
