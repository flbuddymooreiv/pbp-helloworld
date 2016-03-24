import lib.data
import lib.db

_TABLE = 'testtype'
_DBID = 'id'
_APIID = 'id'
_PUT_POST_FIELDS = [
    {'db': 'val', 'api': 'val'}
]


def get(request):
    cur = lib.db.sendtodb('''
        select
            t.id as id,
            t.val as val 
        from %(table)s as t
    ''', {
        'table': lib.db.AsIs(_TABLE),
        'tablestr': _TABLE
    })

    return lib.db.cur2json(cur)


def post(request):
    q = request.forms
    return lib.data.basicinsert(q, _TABLE, _PUT_POST_FIELDS)


def put(request):
    q = request.forms
    return lib.data.basicupdate(q, _TABLE, _DBID, _APIID,
                                _PUT_POST_FIELDS)


def delete(request):
    q = request.forms
    return lib.data.basicdelete(q, _TABLE, _DBID, _APIID)

