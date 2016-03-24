import importlib
import os
import urllib.parse

import urls

import lib.db
import lib.obj
import lib.notify


def init(bottle):

    # PUBLIC CONTENT (NOT PASSWORD PROTECTED!!!)
    for item in lib.obj.any2obj(urls.PUBLIC_STATIC_CONTENT):
        def fun(fname, mtype):
            @bottle.get('/' + fname)
            def get_static_content():
                return bottle.static_file(fname, root='.', mimetype=mtype)
        fun(item.url, item.mimetype)

    for k in lib.obj.any2obj(urls.PUBLIC_DYNAMIC_CONTENT):

        def account_dynamic_routes(mod):
            modname = mod.module if 'module' in dir(mod) else mod.url
            module = importlib.import_module('pages.' + modname)
            url = mod.url

            def do_page(bottle, method):
                return getattr(module, method)(bottle)

            @bottle.get('/' + url)
            def get():
                return do_page(bottle, 'get')

            @bottle.put('/' + url)
            def put():
                return do_page(bottle, 'put')

            @bottle.post('/' + url)
            def post():
                return do_page(bottle, 'post')

            @bottle.delete('/' + url)
            def delete():
                return do_page(bottle, 'delete')
        account_dynamic_routes(k)

    # PASSWORD PROTECTED CONTENT BELOW


    for k in urls.API_HANDLERS:
        def api_routes(mod):
            modname = 'api.' + mod
            module = importlib.import_module(modname)

            def do_api(bottle, method, validperms):
                return getattr(module, method)(bottle.request)

            @bottle.get('/api/' + mod)
            def get():
                return do_api(bottle, 'get', True)

            @bottle.put('/api/' + mod)
            def put():
                return do_api(bottle, 'put', True)

            @bottle.post('/api/' + mod)
            def post():
                return do_api(bottle, 'post', True)

            @bottle.delete('/api/' + mod)
            def delete():
                return do_api(bottle, 'delete', True)

        api_routes(k)

    @bottle.post('/api/_listen')
    def listen():
        config = lib.obj.json2obj(
            bottle.request.body.read().decode('utf-8'))
        for x in lib.notify.waitfornotification(bottle, config):
            yield x
