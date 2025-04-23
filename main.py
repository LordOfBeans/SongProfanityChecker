import oauthlib
import requests
from requests_oauthlib import OAuth2Session
import json
import socket
import webbrowser

# Listens for callback on localhost port 8888
def listenCallback(port):
	sock = socket.socket()
	sock.bind(('', port))
	sock.listen(1)
	conn, address = sock.accept()
	data = conn.recv(1024).decode()
		
	# TODO: Clean up and minimize positional dependencies
	lines = data.splitlines()
	query = lines[0][14:-9]
	if query[:5] != 'code=':
		conn.send('Authorization stage failed. You may close this window.'.encode())
		conn.close()
		sock.close()
		raise Exception('Authorization was not granted')
	conn.send('Authorization stage completed. You may close this window.'.encode())
	conn.close()
	sock.close()
	return query[5:69]


def getAccessToken(client_id, client_secret):
	redirect_uri = 'http://localhost:8888/callback'	

	#  Generate authentication URL
	oauth = OAuth2Session(
		client_id,
		redirect_uri=redirect_uri,
		scope=''
	)
	auth_url, state = oauth.authorization_url(
		'https://api.genius.com/oauth/authorize'
	)

	# Get authentication code from Genius
	webbrowser.open(auth_url)
	auth_code = listenCallback(8888)

	# Get a fresh token
	token = oauth.fetch_token(
		'https://api.genius.com/oauth/token',
		code=auth_code,
		client_secret=client_secret
	)
	return token['access_token']


def songSearch(search, headers):
	api_url = 'https://api.genius.com/search'
	params = {
		'q': search
	}

	resp = requests.get(
		api_url,
		params=params,
		headers=headers
	)
	json_data = json.loads(resp.text)

	hits = json_data['response']['hits']
	print(f'Got {len(hits)} results for {search}')
	for i in range(0, len(hits)):
		hit = hits[i]
		title = hit['result']['full_title']
		print(f'{i+1}. {title}')
	chosen = int(input('Choose a song number: '))
	return hits[chosen-1]['result']


def getSongData(song_id, headers):
	api_url = f'https://api.genius.com/songs/{song_id}/'
	
	resp = requests.get(
		api_url,
		headers=headers
	)
	json_data = json.loads(resp.text)
	return json_data['response']['song']


def getAlbumTracks(album_id, headers):
	api_url = f'https://api.genius.com/albums/{album_id}/tracks'
	
	resp = requests.get(
		api_url,
		headers=headers
	)
	json_data = json.loads(resp.text)
	return json_data['response']['tracks']


def cancelBackslashes(text):
	return_string = ""
	prev_index = 0
	curr_index = 0
	while curr_index >= 0:
		curr_index = text.find('\\', prev_index+1)
		return_string = return_string + text[prev_index:curr_index]
		prev_index = curr_index+1
	return return_string
		

def recursiveAssembleLyrics(curr):
	if isinstance(curr, str):
		return curr
	if 'children' in curr:
		lyric_string = ''
		for child in curr['children']:
			child_lyrics = recursiveAssembleLyrics(child)
			lyric_string = lyric_string + child_lyrics
		return lyric_string
	if 'tag' in curr:
		if curr['tag'] == 'br':
			return '\n'
	return ''

def recursiveCheckProfanity(lyrics, index, curr_trie):
	if index >= len(lyrics):
		if 'endpoint' in curr_trie:
			return ''
		return None
	curr_char = lyrics[index]
	if curr_char not in curr_trie:
		if 'endpoint' in curr_trie:
			return ''
		return None
	recur_result = recursiveCheckProfanity(lyrics, index+1, curr_trie[curr_char])
	if recur_result is not None:
		return curr_char + recur_result
	if 'endpoint' in curr_trie:
		return ''
	return None	

def checkProfanity(lyrics, profanity_trie):
	lyrics = lyrics.lower()
	bad_words = []
	index = 0
	while index < len(lyrics):
		char_result = recursiveCheckProfanity(lyrics, index, profanity_trie)
		if char_result is not None:
			bad_words.append(char_result)
			index += len(char_result)
		else:
			index += 1
	return bad_words
		
	
def scrapeSongLyrics(lyrics_path):
	full_url = 'https://genius.com' + lyrics_path
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0'
	}
	
	resp = requests.get(
		full_url,
		headers=headers
	)
	start_index = resp.text.find("window.__PRELOADED_STATE__ = JSON.parse('")
	end_index = resp.text.find("');\n      window.__APP_CONFIG__")
	json_raw = resp.text[start_index+41:end_index+1]
	json_cancelled = cancelBackslashes(json_raw).strip()
	json_data = json.loads(json_cancelled)
	lyric_data = json_data['songPage']['lyricsData']['body']
	return recursiveAssembleLyrics(lyric_data)	


def main():
	# Get profane words trie
	with open('profanity.json') as f:
		profanity_trie = json.load(f)

	# Retrieve client secrets
	with open('secret.json') as auth_file:
		json_data = json.load(auth_file)
		client_id = json_data['client_id']
		client_secret = json_data['client_secret']

	access_token = getAccessToken(client_id, client_secret)
	headers = {
		'Authorization': f'Bearer {access_token}',
		'Content-Type': 'application/json'
	}

	while True:
		search = input('Enter a song name: ')
		search_result = songSearch(search, headers)
		song_id = search_result['id']
		song_data = getSongData(song_id, headers)
		album_id = song_data['album']['id']
		tracks = getAlbumTracks(album_id, headers)
		for track in tracks:
			track_path = track['song']['path']
			track_name = track['song']['title']
			lyrics = scrapeSongLyrics(track_path)
			profanity_list = checkProfanity(lyrics, profanity_trie)
			print(f'Title: {track_name}')
			count = len(profanity_list)
			print(f'\tProfanity Count: {count}')
			if count > 0:
				profanity_str = ', '.join(profanity_list)
				print(f'\tProfanity: {profanity_str}')
				
			

if __name__ == '__main__':
	main()
