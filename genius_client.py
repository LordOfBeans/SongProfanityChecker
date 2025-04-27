import requests
from requests_oauthlib import OAuth2Session
import webbrowser
import socket
import json
import oauthlib

class GeniusClient:

	def __init__(self, secret_path):
		self.secret_path = secret_path
		self.port = 8888
		self.redirect_uri = f'http://localhost:{self.port}/callback'

	def __listenCallback(self):
		sock = socket.socket()
		sock.bind(('', self.port))
		sock.listen(1)
		conn, address = sock.accept()
		data = conn.recv(1024).decode()

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

	def __getAccessToken(self):
		oauth = OAuth2Session(
			self.client_id,
			redirect_uri = self.redirect_uri,
			scope=''
		)
		auth_url, state = oauth.authorization_url(
			'https://api.genius.com/oauth/authorize'
		)
		webbrowser.open(auth_url)
		auth_code = self.__listenCallback()
		token = oauth.fetch_token(
			'https://api.genius.com/oauth/token',		
			code=auth_code,
			client_secret=self.client_secret
		)
		return token['access_token']

	# TODO: Change approach to avoid using 'with'; get and save access token during init
	def __enter__(self):
		with open(self.secret_path) as f:
			secret_data = json.load(f)
		self.client_id = secret_data['client_id']
		self.client_secret = secret_data['client_secret']
		if 'access_token' in secret_data:
			self.access_token = secret_data['access_token']
		else:
			self.access_token = self.__getAccessToken()
		return self

	def __exit__(self, exc_type, exc_value, tracebrack):
		secrets_dict = {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'access_token': self.access_token
		}	
		with open(self.secret_path, 'w') as f:
			json.dump(secrets_dict, f)

	def __apiCall(self, endpoint, params=None):
		headers = {
			'Authorization': f'Bearer {self.access_token}',
			'Content_Type': 'application/json'
		}
		resp = requests.get(
			'https://api.genius.com' + endpoint,
			params=params,
			headers=headers
		)
		return json.loads(resp.text)['response']

	def songSearch(self, search):
		api_path = '/search'
		params = {
			'q': search
		}

		resp = self.__apiCall(api_path, params=params)
		return resp['hits']

	def getSongData(self, song_id):
		api_path = f'/songs/{song_id}'
		
		resp = self.__apiCall(api_path)
		return resp['song']

	def getAlbumTracks(self, album_id):
		api_path = f'/albums/{album_id}/tracks'

		resp = self.__apiCall(api_path)
		return resp['tracks']

	def __cancelBackslashes(self, text):
		return_string = ""
		prev_index = 0
		curr_index = text.find('\\', prev_index+1)
		while curr_index != -1:
			return_string = return_string + text[prev_index:curr_index]
			prev_index = curr_index + 1
			curr_index = text.find('\\', prev_index + 1)
		return_string = return_string + text[prev_index:]	
		return return_string

	def __recursiveAssembleLyrics(self, curr):
		if isinstance(curr, str):
			return curr
		if 'children' in curr:
			lyric_string = ''
			for child in curr['children']:
				child_lyrics = self.__recursiveAssembleLyrics(child)
				lyric_string = lyric_string + child_lyrics
			return lyric_string
		if 'tag' in curr:
			if curr['tag'] == 'br':
				return '\n'
		return ''

	def scrapeSongLyrics(self, lyrics_path):
		full_url = 'https://genius.com' + lyrics_path
		headers = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.10 Safari/605.1.1' # A very common User-Agent
		}
		resp = requests.get(
			full_url,
			headers=headers
		)
		
		start_index = resp.text.find("window.__PRELOADED_STATE__ = JSON.parse('")
		end_index = resp.text.find("window.__APP_CONFIG__")
		json_raw = resp.text[start_index+41:end_index].strip()[:-3]
		json_cancelled = self.__cancelBackslashes(json_raw).strip()
		json_data = json.loads(json_cancelled)
		lyric_data = json_data['songPage']['lyricsData']['body']
		return self.__recursiveAssembleLyrics(lyric_data)


def main():
	with GeniusClient('secret.json') as genius:
		print('Searching for "Blinding Lights"')
		search_hits = genius.songSearch('Blinding Lights')
		song_id = search_hits[0]['result']['id']
		print('Retrieving song data to get album ID')
		song_data = genius.getSongData(song_id)
		album_id = song_data['album']['id']
		print('Retrieving tracks on album')
		album_tracks = genius.getAlbumTracks(album_id)
		first_track_lyrics_path = album_tracks[0]['song']['path']
		track_info = genius.scrapeSongLyrics(first_track_lyrics_path)	

if __name__ == '__main__': 
	main()
