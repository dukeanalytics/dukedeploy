import json
import os
import re
import requests
import urllib
import tempfile
import cPickle
import re
import inspect
import copy_reg
import marshal
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

# register the reductor to be used for pickling objects of type 'CodeType'
copy_reg.pickle(types.CodeType, reduce_code)

def print_attr(method):  
    obj = '1'#method.im_self  
    cls = '2'#method.im_class  
    ns  = method.__dict__
    print str(ns) +' - '+  obj +' - '+  cls  

def pickle_method(method):  
    func_name = method.im_func.__name__  
    obj = method.im_self  
    cls = method.im_class  
    return _unpickle_method, (func_name, obj, cls)  
  
def unpickle_method(func_name, obj, cls):  
    for cls in cls.mro():  
        try:  
            func = cls.__dict__[func_name]  
        except KeyError:  
            pass  
        else:  
            break  
    return func.__get__(obj, cls)  
  
#copy_reg.pickle(types.MethodType, pickle_method,unpickle_method)  


def check_model_name(name):
    if re.match("^[a-zA-Z0-9_]+$", name):
        return True
    else:
        return False

def check_model_size(model_name):
    size = os.path.getsize(model_name)
    return size

#def predict_udf(model_object,new_data): 
#    return model_object.predict(new_data) 

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
        #print type(model_object)
        if not check_model_name(model_name):
            print 'deploy: model_name must contain alpha-numeric and underscore characters only.'
            return None
        #if predict is None:
        #    predict = predict_udf
        #print predict
        temp_file = tempfile.NamedTemporaryFile(prefix=model_name+'-', suffix='.pkl',mode='w+b+r',delete=False)
        cPickle.dump(model_object,temp_file, protocol=cPickle.HIGHEST_PROTOCOL)
        #print predict.func_code
        #print_attr(predict)
        if predict is None:
            cPickle.dump(None,temp_file, protocol=cPickle.HIGHEST_PROTOCOL)
        else:
            print locals()
            func = types.FunctionType(predict.func_code, globals()) 
            print func
            cPickle.dump(func.func_code,temp_file, protocol=cPickle.HIGHEST_PROTOCOL)
        print temp_file.name
        temp_file.close()
        #print type(predict)
        model_size = check_model_size(temp_file.name) 
        
        if model_size < 25000000:
            dfiles = {'files': (os.path.basename(temp_file.name), open(temp_file.name, 'rb')) }
            data = {'App-ID': self.user_name,
		             'Key': self.api_key}

            r = requests.post('%s/deploy' % self.url, data=data, files=dfiles)
        else:
            print "Model size exceeds 25Mb. Please try to reduce."
            return None

        ####temp_file.close()
        #os.remove(temp_file.name)
    
        if r.status_code != 200:
            print 'deploy: API returned status %s: %s' % (r.status_code, r.text)
            return False
        else:
            print r.text
            return True


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

