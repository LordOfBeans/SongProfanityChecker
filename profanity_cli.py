from db_client import DatabaseClient
import profanity_detection


def createFrequencyDict(profanities, songs):
	detector = profanity_detection.ProfanityClient(profanities, profanities)
	return_dict = {}
	for song in songs:
		lyrics = song[2]
		report = detector.checkLyrics(lyrics)

		concat_results = report.concat_results
		for result in concat_results:
			if result.caught_phrase not in return_dict:
				return_dict[result.caught_phrase] = {
					'total': 0,
					'concat': 0,
					'isolate': 0
				}
			phrase_dict = return_dict[result.caught_phrase]
			phrase_dict['total'] += 1
			phrase_dict['concat'] += 1

		isolate_results = report.isolate_results
		for result in isolate_results:
			if result.caught_phrase not in return_dict:
				return_dict[result.caught_phrase] = {
					'total': 0,
					'concat': 0,
					'isolate': 0
				}
			phrase_dict = return_dict[result.caught_phrase]
			phrase_dict['total'] += 1
			phrase_dict['isolate'] += 1
	return return_dict	

def main():
	profanities = []
	with open('profanity.txt') as f:
		for line in f:
			profanities.append(line.strip())

	with DatabaseClient('database.db') as db:
		songs = db.fetchAllSongs()	

	print(createFrequencyDict(profanities, songs))

if __name__ == '__main__':
	main()
