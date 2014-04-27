'''
Created on Apr 24, 2014

@author: zhil2
'''

from itty import run_itty, get, Response
import time
import subprocess
import os
import json

@get('/')
def welcome(request):
    return Response('Howdy!',
        content_type='text/plain')

@get('/now')
def get_time(request):
    result=time.ctime()
    return Response(result, content_type='text/plain')

@get('/free')
def show_disk_space(request):
    result = subprocess.check_output('du -h', shell=True) #windows chkdsk
    return Response(result, content_type='text/plain')

@get(r'/upper/(?P<word>[A-Za-z]+)')
def to_upper(request,word):
    '''
    Example:
    http://localhost:8000/upper/henry
    HENRY
    '''
    return word.upper()
    #call /upper/raymond

@get(r'/files')
def show_files(request):
    files = os.listdir('.')
    result = json.dumps(files, indent=2)
    return Response(result, content_type='application/json')

# www.google.com/#q=raymond+hettinger

@get(r'/add')
def addition(request):
    '''
    Example:
    http://localhost:8000/add?x=15&y=20
    35
    http://localhost:8000/add?x=15&y=hello
    Malformed request 
    '''
    x = request.GET.get('x', '0')
    y = request.GET.get('y', '0')
    try:
        t = int(x) + int(y)
    except ValueError:
        return Response('Malformed request', status=400)
    result = json.dumps(t)
    return Response(result, content_type='application/json')

'''

http:///www.amazon.com/gp/product/B00j3241
amazon would do

@get(r'/gp/product/?P<prod_id>([A-Z0-9]+)'
def lookup_proudct(request, prod_id):
    c.execute('SELECT info FROM products WHERE prod_id = ?', (prod_id,))
    result = c.fetchall()
    s = format_nice(resutl)
    return Response(s, content_type='text/html')
    
    
http://graph.facebook.com/raymondh

@get(r'/(?P<node>[A-Za-h0-9]+)'
def lookup_user(request, node):
    c.execute('SELECT fieldname, fieldvalue FROM users WHERE node = ?', (node,))
    result = json.dumps(dict(c.fetchall()), indent=2)
    result = Response(s, content_type='application/json')   

'''

if __name__ == '__main__':
    run_itty(host='localhost', port=8000)
