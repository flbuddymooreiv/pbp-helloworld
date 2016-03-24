import bottle
import lib.db


def basicinsert(q, table, fields):

    def insval(apifield):
        return '%(' + apifield + ')s'

    insfields = ','.join([f['db'] for f in fields])
    insvals = ','.join([insval(f['api']) for f in fields])

    query = '''
        insert into %(table)s (%(insfields)s)
        values (''' + insvals + ''')'''

    def paramitem(apifield):
        return {apifield: q[apifield]}

    paramfields = [paramitem(f['api']) for f in fields]

    params = {
        'table': lib.db.AsIs(table),
        'insfields': lib.db.AsIs(insfields),
    }
    for p in paramfields:
        params.update(p)

    (cur, exc) = lib.db.sendtodb(query, params, return_exception=True)

    if not exc:
        return 'ok'
    else:
        bottle.abort(400, exc.pgerror)


def basicupdate(q, table, dbid, apiid, fields):

    if apiid in q and q[apiid]:
        def setitem(dbfield, apifield):
            return dbfield + ' = %(' + apifield + ')s'

        setfields = ','.join([setitem(f['db'], f['api']) for f in fields])

        query = '''
            update %(table)s
            set ''' + setfields + '''
            where %(dbid)s = %(''' + apiid + ''')s'''

        def paramitem(apifield):
            return {apifield: q[apifield]}

        paramfields = [paramitem(f['api']) for f in fields]

        params = {
            'table': lib.db.AsIs(table),
            'setfields': lib.db.AsIs(setfields),
            'dbid': lib.db.AsIs(dbid),
            apiid: q[apiid]
        }
        for p in paramfields:
            params.update(p)

        (cur, exc) = lib.db.sendtodb(query, params, return_exception=True)

        if not exc:
            return 'ok'
        else:
            bottle.abort(400, exc.pgerror)
    else:
        return 'no id'


def basicdelete(q, table, dbid, apiid):

    if apiid in q and q[apiid]:
        (cur, exc) = lib.db.sendtodb('''
            delete from %(table)s where %(dbid)s = %(id)s''' ,
                                     {
                                         'table': lib.db.AsIs(table),
                                         'dbid': lib.db.AsIs(dbid),
                                         'id': q[apiid]
                                     }, return_exception=True)

        if not exc:
            return 'ok'
        else:
            bottle.abort(400, exc.pgerror)
    else:
        return 'no id'
