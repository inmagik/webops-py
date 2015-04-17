import requests

import os
import sys
import logging
import json
import base64

class OpException(Exception):
    def __init__(self, errors_data):
        self.errors_data = errors_data
        return super(OpException, self).__init__()

class HTTPException(Exception):
    def __init__(self, response):
        self.response = response
        return super(HTTPException, self).__init__()


def get_clean_host(host):
    if not host.startswith("http://") and not host.startswith("https://"):
        host = "http://" + host
    return host


def wrap_get(host, url):
    if not url.endswith("/"):
        url += "/"
    h = get_clean_host(host)
    out = requests.get(h+url)
    if out.status_code != 200:
        raise HTTPException(out)
    return out.json()


def wrap_post(host, url):
    if not url.endswith("/"):
        url += "/"
    h = get_clean_host(host)
    out = requests.post(h+url)
    return  out.json()


def get_ops_list(host):
    return wrap_get(host, "/ops")
    


def get_op_meta(host, op):
    url = "/ops/" + op + "/"
    return wrap_get(host, url)


def execute_op(host, op, op_args, outfile=None):          
    h = get_clean_host(host)
    meta = get_op_meta(host, op)
    
    #p = get_parser(meta)
    #print args
    #op_args = p.parse_args(args)
    #print op_args

    #todo: USE A new PARSER
    xargs = zip(*2*[iter(op_args)])
    http_params  ={}
    http_files = {}

    params = meta['parameters']

    for a in xargs:
        pname = a[0].replace("-", "")
        pp = params[pname]
        if pp ['type'] != 'FileField':
            http_params[pname] = a[1]
        else:
            #http_files[pname] = open(a[1], 'rb')
            file_dict = {}
            if a[1].startswith("http"):
                file_dict['data'] = a[1]
                file_dict['filename'] = a[1].split("/")[-1]

            http_params[pname] = file_dict

    #print http_params
    uri = h+"/ops/" + op + "/" 
    
    headers = {'content-type': 'application/json'}
    out = requests.post(uri, json=http_params)
    
    if out.status_code == 200:
        j = out.json()
        
        if meta["output_descriptor"] == 'FileData':
            fname = outfile or j['filename']
            with open(fname, "wb") as outfile:
                outfile.write(base64.b64decode(j['data']))
            return { "result" : fname , "output_descriptor": meta["output_descriptor"] }
        else:
            return { "result" : j , "output_descriptor": meta["output_descriptor"] }

    else:
        errors_data = out.json()
        raise OpException(errors_data)








