from genius_client import GeniusClient
from db_client import DatabaseClient
		
def main():
	with GeniusClient('secret.json') as genius, DatabaseClient('database.db') as db:
		while True:
			search = input('Enter a song name: ')
			hits = genius.songSearch(search)
			print(f'Got {len(hits)} results for {search}')
			for i in range(0, len(hits)):
				hit = hits[i]
				title = hit['result']['full_title']
				print(f'{i+1}. {title}')
			chosen = int(input('Choose a song number: '))
			song_id = hits[chosen-1]['result']['id']
			song_data = genius.getSongData(song_id)
			album_id = song_data['album']['id']
			tracks = genius.getAlbumTracks(album_id)
			for track in tracks:
				track_path = track['song']['path']
				track_name = track['song']['title']
				track_id = track['song']['id']
				lyrics = genius.scrapeSongLyrics(track_path)
				db.addSong(track_id, track_name)
				db.addSongLyrics(track_id, lyrics)
				db.commit()
				print(f'Added {track_name}')

if __name__ == '__main__':
	main()
