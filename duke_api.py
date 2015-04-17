import json
import os
import re
import requests
import urllib
import tempfile
import cPickle
import copy_reg
import types
 
def code_ctor(*args):
    return types.CodeType(*args)

def reduce_code(co):
    if co.co_freevars or co.co_cellvars:
        raise ValueError, "Sorry, cannot pickle code objects from closures"
    return code_ctor, (co.co_argcount, co.co_nlocals, co.co_stacksize,
        co.co_flags, co.co_code, co.co_consts, co.co_names,
        co.co_varnames, co.co_filename, co.co_name, co.co_firstlineno,
        co.co_lnotab)

copy_reg.pickle(types.CodeType, reduce_code)

def check_model_name(name):
    if re.match("^[a-zA-Z0-9_]+$", name):
        return True
    else:
        return False

def check_model_size(model_name):
    size = os.path.getsize(model_name)
    return size


class api:
    def __init__(self, user_name, api_key,api_endpoint, hostname=None):
        if hostname is None:
            hostname='http://deploy.dukeanalytics.com'
        else:
            if '*.dukeanalytics.com' not in hostname:
                return 'deploy: Invalid hostname, please try again.'
        self.url = hostname+api_endpoint
        self.user_name = user_name
        self.api_key = api_key


    def deploy_model(self, model_object,model_name,predict=None):
        if not check_model_name(model_name):
            return json.dumps({"deploy":"deploy: model_name must contain alpha-numeric and underscore characters only."})

        temp_file = tempfile.NamedTemporaryFile(prefix=model_name+'-', suffix='.pkl',mode='w+b+r',delete=False)
        cPickle.dump(model_object,temp_file, protocol=cPickle.HIGHEST_PROTOCOL)

        if predict is None:
            cPickle.dump(None,temp_file, protocol=cPickle.HIGHEST_PROTOCOL)
        else:
            func = types.FunctionType(predict.func_code, globals()) 
            cPickle.dump(func.func_code,temp_file, protocol=cPickle.HIGHEST_PROTOCOL)

        temp_file.close()
        model_size = check_model_size(temp_file.name) 
        
        if model_size < 25000000:
            dfiles = {'files': (os.path.basename(temp_file.name), open(temp_file.name, 'rb')) }

            r = requests.post('%s/deploy/%s/%s' % (self.url,self.user_name,self.api_key), files=dfiles)
        else:
            return json.dumps({"deploy":"Model size exceeds 25Mb. Please try to reduce."})

        temp_file.close()
        os.remove(temp_file.name)
    
        if r.status_code != 200:
            return json.loads(r.text)
        else:
            return json.loads(r.text)


    def predict(self, model_name,new_data):
        new_data_format = json.dumps(new_data.tolist())
        data = {'Model':model_name,'New_Data': new_data_format}
        r = requests.post('%s/predict/%s/%s' % (self.url,self.user_name,self.api_key), data=data)
        if r.status_code != 200:
            return json.loads(r.text)
        else:
            return json.loads(r.text)

        

