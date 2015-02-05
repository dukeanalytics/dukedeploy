import json
import os
import re
import requests
import urllib
import tempfile
import cPickle
import re

def check_model_name(name):
        if re.match("^[a-zA-Z0-9_]+$", name):
            return True
        else:
            return False

class api:
    def __init__(self, user_name, api_key):
        self.url = 'http://deploy.dukeanalytics.com/api/v1.0'
        self.user_name = user_name
        self.api_key = api_key

    def deploy_model(self, model_object,model_name):
        #if not os.path.isfile(filename):
        #print 'sendfile: Error opening file %s' % filename
        #return None
        # need to impose restrictions on model_name
        if not check_model_name(model_name):
            print 'Error: model_name must contain alpha-numeric and underscore characters only.'
            return None
        f3=tempfile.NamedTemporaryFile(prefix=model_name+'-', suffix='.pkl',mode='w+b+r',delete=False)
        cPickle.dump(model_object,f3)
        f3.close()

        dfiles = { 'files': (os.path.basename(f3.name), open(f3.name, 'rb')) }
        data = { 'App-ID': self.user_name,
		         'Key': self.api_key}
        r = requests.post('%s/deploy' % self.url, data=data, files=dfiles)
        if r.status_code != 200:
            print 'deploy: API returned status %s: %s' % (r.status_code, r.text)
            return None
        response_object = json.loads(r.text)
        m = re.match('^The file have been saved as (.*)$', response_object['message'])
        if m:
            return m.groups()[0]
        f3.close()
        
        print 'deploy: cannot save file: %s' % response_object['message']
        return None

    def predict(self, model_name,new_data):
        new_data_format = json.dumps(new_data.tolist())
        data = {'App-ID':self.user_name,'Key':self.api_key,'Ext':'.pkl','Model':model_name,'New_Data': new_data_format}
        r = requests.post('%s/predict' % self.url, data=data)
        if r.status_code != 200:
            print 'predict: API returned status %s: %s' % (r.status_code, r.text)
            return None

        response_object = json.loads(r.text)
		
        if 'message' in response_object:
            print 'predict: message from API: %s' % response_object['message']
            return None

        return response_object

