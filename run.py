#!/usr/bin/env python3

import datetime

import bottle

import routes
import lib.db

lib.db.setconnstr('dbname=helloworld user=postgres')
routes.init(bottle)

app = bottle.app()
app.catchall = False

if __name__ == '__main__':
    bottle.run(host='0.0.0.0', port=8888, app=app)
