import datetime
import json
import select

import dateutil.parser

import lib.db

epoch = datetime.datetime.utcfromtimestamp(0)


def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


def waitfornotification(bottle, config):
    start = datetime.datetime.utcnow()

    # TODO: all kinds of validation

    # TODO: this is a bit sloppy in that the config isn't factored
    # into the mtime query. As a result, records we don't care about
    # could cause a short circuit. Not as bad as the blocking calls
    # below, but still could probably offer enhancement. On the flip
    # side, since the query is simple, it will complete quickly
    # whereas making it tight with configs may cause it to be slow
    # on evey long poll initiation.
    shortcircuit = []
    for i, c in enumerate(config):
        if 'laterthan' in dir(c):
            threshold = float(c.laterthan)
            for t in c.types:
                table = t.type
                cur = lib.db.sendtodb('''
                    select 
                        (select mtime from %(asistable)s
                            order by mtime desc limit 1) as rowmtime, 
                        (select mtime from table_mtime 
                            where name = %(table)s) as tablemtime
                ''', {
                    'asistable': lib.db.AsIs(table),
                    'table': table
                })

                row = dict(list(cur)[0])
                rowmtime = row['rowmtime']
                tablemtime = row['tablemtime']

                latest = unix_time_millis(max(rowmtime, tablemtime))

                if latest and latest > threshold:
                    shortcircuit += [{
                        'i': i,
                        'mtime': latest
                    }]

    if shortcircuit:
        yield json.dumps(shortcircuit)
        return

    def tablelisten(t):
        return '''
            listen ''' + t + '''_insert;
            listen ''' + t + '''_update;
            listen ''' + t + '''_delete;
        '''

    keys = []
    for c in config:
        for t in c.types:
            keys += [t.type]

    listens = '\n'.join([tablelisten(k) for k in keys])

    conn = lib.db.getsingleconn()

    cur = conn.cursor()
    cur.execute('''begin; ''' + listens + ''' commit;''')

    while True:
        # Give WSGI something to crash on if the client disconnects
        # so we can tear down the db connection rather than let it time out
        yield ' '

        if select.select([conn.fileno()], [], [], 1) == ([], [], []):
            if (datetime.datetime.utcnow() - start).seconds >= 30:
                conn.close()
                yield json.dumps([])
                break

        conn.poll()

        if len(conn.notifies) > 0:
            ret = []
            for note in conn.notifies:
                payload = lib.obj.json2obj(note.payload)
                table = (note.channel.replace('_update', '')
                         .replace('_insert', '')
                         .replace('_delete', '')
                         )

                typename = table

                for (i, cfg) in enumerate(config):
                    tableconfigs = [c for c in cfg.types
                                    if c.type == typename]

                    if tableconfigs:
                        tableconfig = tableconfigs[0]
                        if note.channel.endswith('_update'):
                            oldpayload = payload.old
                            newpayload = payload.new
                            if 'constraints' in dir(tableconfig):
                                for f in tableconfig.constraints._fields:
                                    v = getattr(tableconfig.constraints, f)
                                    if f in oldpayload._fields:
                                        if getattr(oldpayload, f) == v:
                                            t = dateutil.parser.parse(
                                                oldpayload.mtime)
                                            ret += [{
                                                'i': i,
                                                'mtime': unix_time_millis(t)
                                            }]
                                    if f in newpayload._fields:
                                        if getattr(newpayload, f) == v:
                                            t = dateutil.parser.parse(
                                                newpayload.mtime)
                                            ret += [{
                                                'i': i,
                                                'mtime': unix_time_millis(t)
                                            }]
                            else:
                                ret += [{
                                    'i': i,
                                    'mtime': newpayload.mtime
                                }]
                        else:
                            if 'constraints' in dir(tableconfig):
                                for f in tableconfig.constraints._fields:
                                    v = getattr(tableconfig.constraints, f)
                                    if f in payload._fields:
                                        if getattr(payload, f) == v:
                                            t = dateutil.parser.parse(
                                                payload.mtime)
                                            ret += [{
                                                'i': i,
                                                'mtime': unix_time_millis(t)
                                            }]
                            else:
                                t = dateutil.parser.parse(payload.mtime)
                                ret += [{
                                    'i': i,
                                    'mtime': unix_time_millis(t)
                                }]

            conn.notifies.clear()
            if ret:
                conn.close()
                yield json.dumps(ret)
                break
