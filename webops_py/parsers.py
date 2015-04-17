import argparse

def get_parser(op_meta):
    #print op_meta
    p = argparse.ArgumentParser(description=op_meta['description'])
    params = op_meta['parameters']
    for param in params:
        if params[param]['required']:
            nargs = '?'
            required = True
        else:
            nargs = '?'
            required = False
        p.add_argument(param, nargs=nargs)
    return p