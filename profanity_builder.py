import json

def main():
	profane_phrases = []
	with open('profanity.txt') as file:
		for line in file:
			profane_phrases.append(line.strip())
	profane_sorted = sorted(profane_phrases)

	profane_trie = {}
	for phrase in profane_sorted:
		curr_level = profane_trie
		for char in phrase:
			if char not in curr_level:
				curr_level[char] = {}
			curr_level = curr_level[char]
		curr_level['endpoint'] = True

	with open('profanity.json', 'w') as file:
		json.dump(profane_trie, file)

if __name__ == '__main__':
	main()
