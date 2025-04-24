import string

class Profanity:

	def __init__(self, lyrics, phrase_indices, line_indices, profanity_level):
		self.lyrics = lyrics # Pointer to the original lyrics
		self.phrase_indicies = phrase_indicies
		self.line_indices = line_indices
		self.profanity_level = profanity_level


class ConcatenationDetector:

	def __init__(self):
		self.trie = {}
		self.remove_chars = f'{string.punctuation}{string.whitespace}'

	def addProfanity(self, profanity, profanity_level):
		curr_level = self.trie
		for char in profanity:
			if char not in curr_level:
				curr_level[char] = {}
			curr_level = curr_level[char]
		curr_level['level'] = profanity_level	

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
	
	def __recursiveCheck(self, concat_lyrics, index, curr_trie):
		if index >= len(concat_lyrics):
			if 'level' in curr_trie: # Edge case
				return '', curr_trie['level']
			return None, None
		curr_char = concat_lyrics[index]
		if curr_char not in curr_trie:
			if 'level' in curr_trie:
				return '', curr_trie['level']
			return None, None
		
		
			
		
	
	def checkLyrics(self, lyrics):
		lyrics = lyrics.lower()
		concat_lyrics = self.__concatLyrics(lyrics)
		


class ProfanityClient:

	def __init__(self, profanities, profanity_levels):
		self.profanities = profanities
		self.profanity_level = profanity_levels


def main():
	cd = ConcatenationDetector()
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
	print(cd.concatLyrics(lyrics))

if __name__ == '__main__':
	main()
