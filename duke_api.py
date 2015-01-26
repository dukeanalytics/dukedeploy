import json
import os
import re
import requests
import urllib

class api:
	def __init__(self, username, api_key):
		self.url = 'http://deploy.dukeanalytics.com/api/v1.0'
		self.username = username
		self.api_key = api_key
	
	def deploymodel(self, filename):
		if not os.path.isfile(filename):
			print 'sendfile: Error opening file %s' % filename
			return None

		files = { 'files': (os.path.basename(filename), open(filename, 'r')) }
		data = { 'App-ID': self.username,
		         'Key':    self.api_key,
		       }
		r = requests.post('%s/upload' % self.url, data=data, files=files)
		if r.status_code != 200:
			print 'sendfile: API returned status %s: %s' % (r.status_code, r.text)
			return None

		response_object = json.loads(r.text)
		m = re.match('^The file have been saved as (.*)$', response_object['message'])
		if m:
			return m.groups()[0]

		print 'sendfile: cannot save file: %s' % response_object['message']
		return None
	
	def getmodel(self, filename):
		get_url = '%s/content/%s/%s/%s' % (self.url, 
		                                   urllib.quote(self.username), 
						   urllib.quote(self.api_key), 
						   urllib.quote(filename))
		
		r = requests.get(get_url)
		if r.status_code != 200:
			print 'getfile: API returned status %s: %s' % (r.status_code, r.text)
			return None

		response_object = json.loads(r.text)
		if 'message' in response_object:
			print 'getfile: message from API: %s' % response_object['message']
			return None

		if not ('file_content' in response_object):
			print 'getfile: response does not contain file_content'
			return None

		return response_object['file_content']

	def predict(self, jdata):
		"TODO"
	

