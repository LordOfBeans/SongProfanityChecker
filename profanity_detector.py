import string

class Profanity:

	def __init__(self, caught_phrase, lyrics, start_index, end_index):
		self.caught_phrase = caught_phrase # Raw lowercase phrase that was matched
		self.lyrics = lyrics # Pointer to the original lyrics
		self.start_index = start_index # Start index in original lyrics
		self.end_index = end_index # End index in original lyrics

	# Returns full line with profane phrase
	def getLine(self):
		prev_break = self.lyrics.rfind('\n', 0, self.start_index)
		if prev_break == -1:
			prev_break = 0
		next_break = self.lyrics.find('\n', self.end_index)
		if next_break == -1:
			next_break = len(self.lyrics)
		return self.lyrics[prev_break:next_break].strip()
		

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
				profanity = Profanity(checked, lyrics, true_start_index, true_end_index)
				profanities.append(profanity)
		return profanities
			

class ProfanityClient:

	def __init__(self, concat_profanities, isolate_profanities):
		self.concat_profanities = concat_profanities
		self.isolate_profanities = isolate_profanities

		self.concat_checker = ConcatenationDetector()
		for phrase in concat_profanities:
			self.concat_checker.addProfanity(phrase)		

	def checkLyrics(self, lyrics):
		concat_results = self.concat_checker.checkLyrics(lyrics)
		return concat_results
		

def main():
	concat_profanities = ['igot', 'porsche', 'toma', 'hevall', 'chnow']
	isolate_profanities = []

	client = ProfanityClient(concat_profanities, isolate_profanities)
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
	results = client.checkLyrics(lyrics)
	for item in results:
		caught = item.caught_phrase
		line = item.getLine()
		print(f'Caught "{caught}" in "{line}"')


if __name__ == '__main__':
	main()
