import string
from menu_utils import spacePadString

OVERLAP_TYPES = ['concatenation only', 'isolation only', 'subword only', 'simple overlap', 'complex overlap']

class Profanity:

	def __init__(self, caught_phrase, lyrics, start_index, end_index, detection_method):
		self.caught_phrase = caught_phrase # Raw lowercase phrase that was matched
		self.lyrics = lyrics # Pointer to the original lyrics
		self.start_index = start_index # Start index in original lyrics
		self.end_index = end_index # End index in original lyrics
		self.detection_method = detection_method

	# Returns full line with profane phrase
	def getLine(self):
		prev_break = self.lyrics.rfind('\n', 0, self.start_index)
		if prev_break == -1:
			prev_break = 0
		next_break = self.lyrics.find('\n', self.end_index)
		if next_break == -1:
			next_break = len(self.lyrics)
		return self.lyrics[prev_break:next_break].strip()

# Best for profane phrases that don't occur frequently within or between other words
# Necessary for profanities that are a concatenation of two words
class ConcatenationDetector:

	def __init__(self):
		self.trie = {}
		self.remove_chars = f'{string.punctuation}{string.whitespace}'

	def addProfanity(self, profanity):
		curr_level = self.trie
		for char in profanity:
			if char not in curr_level:
				curr_level[char] = {}
			curr_level = curr_level[char]
		curr_level['endnode'] = True

	# Returns lyrics without whitespace or punctuation
	def __concatLyrics(self, lyrics):
		return_string = ''
		array_map = []
		for i in range(0, len(lyrics)):
			curr_char = lyrics[i]
			if curr_char not in self.remove_chars:
				return_string += curr_char
				array_map.append(i)
		return return_string, array_map

	# Returns maximum length profanity starting at certain index
	# Returns None if no profanity is found	
	def __recursiveCheck(self, concat_lyrics, index, curr_trie):
		if index >= len(concat_lyrics):
			if 'endnode' in curr_trie: # Edge case
				return ''
			return None
		curr_char = concat_lyrics[index]
		if curr_char not in curr_trie:
			if 'endnode' in curr_trie:
				return ''
			return None
		recur_result = self.__recursiveCheck(concat_lyrics, index+1, curr_trie[curr_char])
		if recur_result is not None:
			return curr_char + recur_result
		if 'endnode' in curr_trie:
			return ''
		return None 
				
	def checkLyrics(self, lyrics):
		lower_lyrics = lyrics.lower()
		concat_lyrics, array_map = self.__concatLyrics(lower_lyrics)

		profanities = [] # Contains Profanity objects
		for i in range(0, len(concat_lyrics)):
			checked = self.__recursiveCheck(concat_lyrics, i, self.trie)
			if checked is not None:
				concat_end_index = i + len(checked) - 1
				true_start_index = array_map[i]
				true_end_index = array_map[concat_end_index] + 1
				profanity = Profanity(checked, lyrics, true_start_index, true_end_index, 'concatenation')
				profanities.append(profanity)
		return profanities


# Necessary for accurately detecting profanities that frequently appear within other words
# Will need to include the plural forms of these profanities as well
class IsolationDetector:

	def __init__(self):
		self.profanity_list = [] # Contains strings
		self.keep_characters = f'{string.ascii_lowercase}{string.digits}' # Digits could be useful in rare instances

	def addProfanity(self, phrase):
		if phrase not in self.profanity_list:
			self.profanity_list.append(phrase)

	def __isolateLyricWords(self, lyrics):
		lyric_words = []
		array_map = [] # For each word, this array holds its starting position in the original lyrics
		curr_word = ''
		for i in range(0, len(lyrics)):
			curr_char = lyrics[i]
			if curr_char in self.keep_characters:
				curr_word += curr_char
			else:
				if curr_word != '':
					lyric_words.append(curr_word)
					array_map.append(i - len(curr_word))
					curr_word = ''
		if curr_word != '': # In case lyrics end in a word
			lyric_words.append(curr_word)
			array_map.append(len(lyrics) - len(curr_word))
		return lyric_words, array_map

	def checkLyrics(self, lyrics):
		lower_lyrics = lyrics.lower()
		lyric_words, array_map = self.__isolateLyricWords(lower_lyrics)

		profanities = [] # Contains Profanity objects for detected profane words
		for i in range(0, len(lyric_words)):
			curr_word = lyric_words[i]
			if curr_word in self.profanity_list:
				start_index = array_map[i]
				end_index = start_index + len(curr_word)
				profanity = Profanity(curr_word, lyrics, start_index, end_index, 'isolation')
				profanities.append(profanity)
		return profanities

# TODO: Consider way to combin this with ConcatenationDetector
# Good for words that produce false positives with concatenation but are infrequently embedded in indiviual words
class SubwordDetector:
					
	def __init__(self):
		self.trie = {}
		self.remove_chars = f'{string.punctuation}{string.whitespace}'
		self.keep_characters = f'{string.ascii_lowercase}{string.digits}' # Digits could be useful in rare instances

	def addProfanity(self, profanity):
		curr_level = self.trie
		for char in profanity:
			if char not in curr_level:
				curr_level[char] = {}
			curr_level = curr_level[char]
		curr_level['endnode'] = True

	def __isolateLyricWords(self, lyrics):
		lyric_words = []
		array_map = [] # For each word, this array holds its starting position in the original lyrics
		curr_word = ''
		for i in range(0, len(lyrics)):
			curr_char = lyrics[i]
			if curr_char in self.keep_characters:
				curr_word += curr_char
			else:
				if curr_word != '':
					lyric_words.append(curr_word)
					array_map.append(i - len(curr_word))
					curr_word = ''
		if curr_word != '': # In case lyrics end in a word
			lyric_words.append(curr_word)
			array_map.append(len(lyrics) - len(curr_word))
		return lyric_words, array_map

	# Returns maximum length profanity starting at certain index
	# Returns None if no profanity is found	
	def __recursiveCheck(self, concat_lyrics, index, curr_trie):
		if index >= len(concat_lyrics):
			if 'endnode' in curr_trie: # Edge case
				return ''
			return None
		curr_char = concat_lyrics[index]
		if curr_char not in curr_trie:
			if 'endnode' in curr_trie:
				return ''
			return None
		recur_result = self.__recursiveCheck(concat_lyrics, index+1, curr_trie[curr_char])
		if recur_result is not None:
			return curr_char + recur_result
		if 'endnode' in curr_trie:
			return ''
		return None 

	def checkLyrics(self, lyrics):
		lower_lyrics = lyrics.lower()
		lyric_words, array_map = self.__isolateLyricWords(lower_lyrics)

		profanities = [] # Contains Profanity objects for detected profane words
		for i in range(0, len(lyric_words)):
			curr_word = lyric_words[i]
			for j in range(0, len(curr_word)):
				checked = self.__recursiveCheck(curr_word, j, self.trie)
				if checked is not None:
					true_start_index = array_map[i] + j
					true_end_index = array_map[i] + j + len(checked)
					profanity = Profanity(checked, lyrics, true_start_index, true_end_index, 'subword')
					profanities.append(profanity)
		return profanities

class ProfanityClient:

	def __init__(self, concat_profanities, isolate_profanities, subword_profanities, profanity_level, level_penalty):
		self.concat_profanities = concat_profanities
		self.isolate_profanities = isolate_profanities
		self.subword_profanities = subword_profanities
		self.profanity_level = profanity_level # Dict w/ profanities as keys and level names as values
		self.level_penalty = level_penalty # Dict w/ level names as keys and penalty integers as values

		self.concat_checker = ConcatenationDetector()
		for phrase in self.concat_profanities:
			self.concat_checker.addProfanity(phrase)

		self.isolate_checker = IsolationDetector()
		for phrase in self.isolate_profanities:
			self.isolate_checker.addProfanity(phrase)

		self.subword_checker = SubwordDetector()
		for phrase in self.subword_profanities:
			self.subword_checker.addProfanity(phrase)

	# Allows users to examine profanity in any given song at varying levels
	class ProfanityReport:

		# Profanity reports are primarily made up of the overlap groups in each song
		class OverlapGroup:

			def __init__(self, lyrics, profanities):
				self.lyrics = lyrics
				self.profanities = profanities				

			def getType(self):
				if len(self.profanities) == 1:
					if self.profanities[0].detection_method == 'concatenation':
						return 'concatenation only'
					elif self.profanities[0].detection_method == 'isolation':
						return 'isolation only'
					elif self.profanities[0].detection_method == 'subword':
						return 'subword only'
				else:
					start_index = self.profanities[0].start_index
					end_index = self.profanities[0].end_index
					for i in range(1, len(self.profanities)):
						curr_profanity = self.profanities[i]
						if curr_profanity.start_index != start_index or curr_profanity.end_index != end_index:
							return 'complex overlap'
					return 'simple overlap'

			# Returns a dictionary with each unique profane phrase in overlap and its count
			# This function is really meant for complex overlaps, which may contain simple overlaps
			def countProfanities(self):
				sorted_overlap = sorted(self.profanities, key=lambda x: (x.start_index, x.end_index)) # Identical indices end up adjacent
				return_dict = {
					sorted_overlap[0].caught_phrase: 1
				}
				prev_start = sorted_overlap[0].start_index
				prev_end = sorted_overlap[0].end_index
				for i in range(1, len(sorted_overlap)):
					curr_profanity = sorted_overlap[i]
					if curr_profanity.start_index != prev_start or curr_profanity.end_index != prev_end:
						if curr_profanity.caught_phrase not in return_dict:
							return_dict[curr_profanity.caught_phrase] = 0
						return_dict[curr_profanity.caught_phrase] += 1
						prev_start = curr_profanity.start_index
						prev_end = curr_profanity.end_index
				return return_dict

			# space_padding argument doesn't function with __str__()
			def toString(self, space_padding=4):
				overlap_type = self.getType()
				if overlap_type in ['concatenation only', 'isolation only', 'subword only']:
					phrase = self.profanities[0].caught_phrase
					method = self.profanities[0].detection_method
					context = spacePadString(self.profanities[0].getLine(), space_padding)
					return f'Phrase: {phrase}\nDetection Method: {method}\nContext:\n{context}'
				elif overlap_type == 'simple overlap':
					phrase = self.profanities[0].caught_phrase
					methods = []
					for item in self.profanities:
						methods.append(item.detection_method)
					methods_str = ', '.join(methods)
					context = spacePadString(self.profanities[0].getLine(), space_padding)
					return f'Phrase: {phrase}\nDetection Methods: {methods_str}\nContext:\n{context}'
				elif overlap_type == 'complex overlap':
					sorted_overlap = sorted(self.profanities, key=lambda x: x.start_index)
					max_end = sorted_overlap[0].end_index
					phrases = [sorted_overlap[0].caught_phrase]
					methods_str = f'Detected {sorted_overlap[0].caught_phrase} via {sorted_overlap[0].detection_method}'
					for i in range(1, len(sorted_overlap)):
						phrases.append(sorted_overlap[i].caught_phrase)
						methods_str += f'\nDetected {sorted_overlap[i].caught_phrase} via {sorted_overlap[i].detection_method}'
						if sorted_overlap[i].end_index > max_end:
							max_end = sorted_overlap[i].end_index
					phrases_str = ', '.join(phrases)
					methods_str = spacePadString(methods_str, space_padding)
					prev_break = self.lyrics.rfind('\n', 0, sorted_overlap[0].start_index)
					if prev_break == -1:
						prev_break = 0
					next_break = self.lyrics.find('\n', max_end)
					if next_break == -1:
						next_break = len(self.lyrics)
					context = spacePadString(self.lyrics[prev_break:next_break].strip(), space_padding)
					return f'Phrases: {phrases_str}\nDetection Methods:\n{methods_str}\nContext:\n{context}'


		def __init__(self, lyrics, concat_results, isolate_results, subword_results, profanity_level, level_penalty):
			self.lyrics = lyrics
			self.concat_results = concat_results
			self.isolate_results = isolate_results
			self.subword_results = subword_results
			self.profanity_level = profanity_level
			self.level_penalty = level_penalty

			# Finds any instances where caught phrases overlap with others
			full_results = self.concat_results + self.isolate_results + self.subword_results
			self.groups = []
			if len(full_results) == 0: # Can't make overlap groups with zero profanities
				return
			sorted_results = sorted(full_results, key=lambda x: x.start_index)
			curr_overlap = [sorted_results[0]]
			max_end = sorted_results[0].end_index
			for i in range(1, len(sorted_results)):
				curr_profanity = sorted_results[i]
				curr_start = curr_profanity.start_index
				if curr_start < max_end: # Overlap detected
					curr_overlap.append(curr_profanity)
					if curr_profanity.end_index > max_end:
						max_end = curr_profanity.end_index
				else: # Save current group and reset if no overlap
					new_overlap_group = self.OverlapGroup(self.lyrics, curr_overlap)
					self.groups.append(new_overlap_group)
					curr_overlap = [curr_profanity]
					max_end = curr_profanity.end_index
			new_overlap_group = self.OverlapGroup(self.lyrics, curr_overlap)
			self.groups.append(new_overlap_group)

		# Returns a dictionary with profanity counts, sources, and overlap groups
		def getProfanityCounts(self):
			return_dict = {
				'total_penalty': 0,
				'profanities': {}
			}
			profanities_dict = return_dict['profanities']
			for group in self.groups:
				group_profanities = group.countProfanities()
				group_type = group.getType()
				for phrase, count in group_profanities.items():
					phrase_level = self.profanity_level[phrase]
					if phrase not in profanities_dict:
						profanities_dict[phrase] = {
							'count': 0,
							'penalty': 0,
							'level': phrase_level
						}
						for overlap_type in OVERLAP_TYPES:
							profanities_dict[phrase][overlap_type] = { # Re-initialized for every iteration of the loop
								'count': 0,
								'groups': []
							}
					phrase_dict = profanities_dict[phrase]
					phrase_dict['count'] += count
					penalty_total = self.level_penalty[phrase_level] * count
					return_dict['total_penalty'] += penalty_total
					phrase_dict['penalty'] += penalty_total
					phrase_dict[group_type]['count'] += count
					phrase_dict[group_type]['groups'].append(group)
			return return_dict

		def toString(self, space_padding=4):
			profanity_counts = self.getProfanityCounts()
			return_str = ''
			profanities_dict = profanity_counts['profanities']
			for phrase, info in sorted(profanities_dict.items(), key=lambda x: x[0]): # Sorts alphabetically
				total_found = info['count']
				level = info['level']
				penalty = info['penalty']
				return_str += f'Phrase: {phrase}'
				next_level = f'\nLevel: {level}\nCount: {total_found}\nPenalty: {penalty}\nOverlap Types:\n'
				methods_str = ''
				example_count = 0
				examples_str = ''
				for method in OVERLAP_TYPES:
					method_count = info[method]['count']
					if method_count > 0:
						methods_str += f'{method}: {method_count}\n'
						for group in info[method]['groups']:
							example_count += 1
							group_str = spacePadString(group.toString(space_padding), space_padding)
							examples_str += f'Example {example_count}:\n{group_str}\n'
				next_level += spacePadString(methods_str, space_padding)
				return_str += spacePadString(next_level, space_padding)
				next_level = 'Examples:\n'
				next_level += spacePadString(examples_str, space_padding)
				return_str += spacePadString(next_level, space_padding)
			total_penalty = profanity_counts['total_penalty']
			return_str = spacePadString(return_str, space_padding)
			return_str = f'Total Penalty: {total_penalty}\nProfanities:\n' + return_str
			return return_str[:-1]	

	def checkLyrics(self, lyrics):
		concat_results = self.concat_checker.checkLyrics(lyrics)
		isolate_results = self.isolate_checker.checkLyrics(lyrics)
		subword_results = self.subword_checker.checkLyrics(lyrics)
		return self.ProfanityReport(lyrics, concat_results, isolate_results, subword_results, self.profanity_level, self.level_penalty)

# Takes profanities found in individual songs and totals them up, returns dictionary
def combineProfanityReports(reports):
	return_dict = {}
	for report in reports:
		report_counts = report.getProfanityCounts()
		for phrase, info in report_counts.items():
			# Mirrors ProfanityClient.ProfanityReport.getProfanityCounts()
			if phrase not in return_dict:
				return_dict[phrase] = {
					'total': 0
				}
				for overlap_type in OVERLAP_TYPES:
					return_dict[phrase][overlap_type] = { # Re-initialized for every iteration of the loop
						'count': 0,
						'groups': []
				}
			phrase_dict = return_dict[phrase]
			phrase_dict['total'] += info['total']
			for overlap_type in OVERLAP_TYPES:
				phrase_dict[overlap_type]['count'] += info[overlap_type]['count']
				phrase_dict[overlap_type]['groups'] += info[overlap_type]['groups']
	return return_dict	
	
def main():
	concat_profanities = ['chrid', 'porsche', 'toma', 'chnow', 'in'] # Not gonna allow any actual profanity in this repo
	isolate_profanities = ['horse', 'now', 'in', 'match', 'porsche']
	subword_profanities = ['orse', 'sesin', 'porsche']
	profanity_level = {
		'sesin': 'ok',
		'chrid': 'medium',
		'porsche': 'worse',
		'toma': 'worst',
		'orse': 'ok',
		'chnow': 'medium',
		'in': 'worse',
		'horse': 'worst',
		'now': 'ok',
		'match': 'medium'
	}
	level_penalty = {
		'ok': 1,
		'medium': 2,
		'worse': 4,
		'worst': 8
	}

	client = ProfanityClient(concat_profanities, isolate_profanities, subword_profanities, profanity_level, level_penalty)
	lyrics = """
I got the horses in the back
Horse tack is attached
Hat is matte black
Got the boots that's black to match
Ridin' on a horse, ha
You can whip your Porsche
I been in the valley
You ain't been up off that porch, now
	"""
	report = client.checkLyrics(lyrics)
	print(report.toString())

if __name__ == '__main__':
	main()
