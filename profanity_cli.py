from db_client import DatabaseClient
from profanity_detection import ProfanityClient, combineProfanityReports, OVERLAP_TYPES
from menu_utils import pickInteger, spacePadString

SPACE_PADDING = 4


# --- UTILITY / HELPER FUNCTIONS --- #

# Used in evaluateNewProfanitiesMenu()
# If phrase is already in profanities table, we can skip it
# If another phrase in profanities table with either concatenation or subword detection is a substring of current phrase, skip current phrase
# Helps ensure minimal work is done by both user and client
def checkSkipProfanity(db_cur, phrase):
	db_profanities = db_cur.fetchAllProfanities()
	for db_phrase in db_profanities:
		if db_phrase[0] == phrase:
			return db_phrase[0]
		elif db_phrase[2] in ['concatenation', 'subword'] and db_phrase[0] in phrase:
			return db_phrase[0]
	return None

# --- MENU FUNCTIONS --- #

def addProfanityLevelMenu(db_cur):
	print('\nADD PROFANITY LEVEL')
	name = input('Enter name: ')
	if name.strip() == '':
		print('New profanity level was cancelled')
		return False
	points = int(input('Enter integer points: '))
	db_cur.addProfanityLevel(name, points)
	return True

def additionalContextMenu(phrase, info):
	print(f'\nADDITIONAL CONTEXT for {phrase}')
	print('0. Go Back')
	for i in range(0, len(OVERLAP_TYPES)):
		curr_type = OVERLAP_TYPES[i]
		curr_count = info[curr_type]['count']
		print(f'{i+1}. View cases of {curr_type} ({curr_count})')
	choice = pickInteger(0, len(OVERLAP_TYPES))
	if choice == 0:
		return
	chosen_type = OVERLAP_TYPES[choice - 1]
	
	print('\nExamples:')
	groups = info[chosen_type]['groups']
	for i in range(0, len(groups)):
		print(spacePadString(f'Example {i+1}:', SPACE_PADDING))
		curr_group = groups[i]
		print(spacePadString(curr_group.toString(), SPACE_PADDING * 2)) 	

# Returns True if user chose a profanity level, otherwise False
# Performs insertion of profane phrase into database
def evaluatePhraseMenuTwo(db_cur, phrase, info, method):	
	levels = sorted(db_cur.fetchProfanityLevels(), key=lambda x: x[1]) # Sort by points ascending

	print(f'\nEVALUATION STAGE TWO OPTIONS for {phrase}')
	print('0. Go Back')
	for i in range(0, len(levels)):	
		curr = levels[i]
		name = curr[0]
		points = curr[1]
		print(f'{i+1}. Assign Level -- {name} ({points} points)')
	choice = pickInteger(0, len(levels))
	if choice == 0:
		return False
	chosen_level = levels[choice - 1]
	db_cur.addProfanity(phrase, chosen_level[0], method)
	return True
	
# Returns True if user chooses to quit evaluating phrases, otherwise False
def evaluatePhraseMenuOne(db_cur, phrase, info):
	print(f'Phrase: {phrase}')
	total = info['total']
	print(f'Total: {total}')
	print('Overlap Statistics:')
	for overlap_type in OVERLAP_TYPES:
		overlap_count = info[overlap_type]['count']
		print(spacePadString(f'{overlap_type}: {overlap_count}', SPACE_PADDING))

	while True:
		print(f'\nEVALUATION STAGE ONE OPTIONS for {phrase}')
		print('0. Quit Evaluating')
		print('1. Assign Subword-based Detection')
		print('2. Assign Isolation-based Detection')
		print('3. Assign Concatenation-based Detection')
		print('4. View Additional Context') 
		print('5. Skip')
		choice = pickInteger(0, 5)
		if choice == 0:
			return True
		elif choice == 1:
			if evaluatePhraseMenuTwo(db_cur, phrase, info, 'subword'):
				break
		elif choice == 2:
			if evaluatePhraseMenuTwo(db_cur, phrase, info, 'isolation'):
				break
		elif choice == 3:
			if evaluatePhraseMenuTwo(db_cur, phrase, info, 'concatenation'):
				break
		elif choice == 4:
			additionalContextMenu(phrase, info)
		elif choice == 5:
			break	

def evaluateNewProfanitiesMenu(db_cur):
	print('\nEVALUATE NEW PROFANITIES')

	# Set up profanity detector
	print('Reading list of profane phrases...')
	profanities = []
	with open('profanity.txt') as f:
		for line in f:
			profanities.append(line.strip().lower()) # Profanities get converted to lowercase
	profanity_detector = ProfanityClient(profanities, profanities, profanities) # Use both methods for each profanity; done purely for evaluation

	# Get data based on all songs in database
	print('Retrieiving all song lyrics from database...')
	songs = db_cur.fetchAllSongs()
	print('Checking each song for profanities...')
	reports = []
	for song in songs:
		lyrics = song[2]
		reports.append(profanity_detector.checkLyrics(lyrics))
	print('Combining results and sorting...')
	combined_dict = combineProfanityReports(reports)
	sorted_items = sorted(combined_dict.items(), key=lambda x: x[1]['total'], reverse=True) # Sort by total found
	unique_count = len(sorted_items)
	print(f'Found {unique_count} unique profane phrases across all songs')

	# Have user choose how to categorize each profanity
	for i in range(0, unique_count):
		phrase = sorted_items[i][0]
		skippable = checkSkipProfanity(db_cur, phrase)
		if skippable is not None:
			print(f'\nSkipped evaluation of "{phrase}" due to overlap with "{skippable}"')
			continue
		info = sorted_items[i][1]
		print(f'\nEVALUATE PROFANITY {i+1} of {unique_count}')
		if evaluatePhraseMenuOne(db_cur, phrase, info):
			break		

def mainMenu(db_cur):
	while True:
		print('\nMAIN MENU')
		print('0. Commit and Quit')
		print('1. Add Profanity Level')
		print('2. Evaluate New Profanities')
		print('3. Clear All Profanities')
		choice = pickInteger(0, 3)
		if choice == 0:
			db_cur.commit()
			return
		elif choice == 1:
			addProfanityLevelMenu(db_cur)
		elif choice == 2:
			evaluateNewProfanitiesMenu(db_cur)
		elif choice == 3:
			db_cur.clearAllProfanities()

def main():
	with DatabaseClient('database.db') as db_cur:
		mainMenu(db_cur)

if __name__ == '__main__':
	main()
