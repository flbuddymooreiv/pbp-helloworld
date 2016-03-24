import copy
import json
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import psycopg2.pool
import traceback


def setconnstr(connstr):
    setconnstr.CONN_STR = connstr
    if 'POOL' not in dir(setconnstr):
        setconnstr.POOL = psycopg2.pool.ThreadedConnectionPool(
            8, 512, setconnstr.CONN_STR)


def getsingleconn():
    return psycopg2.connect(setconnstr.CONN_STR)


def conntodb():
    success = False
    while not success:
        try:
            curconn = setconnstr.POOL.getconn()
            success = True
        except psycopg2.pool.PoolError as pe:
            pass
    return curconn


def disconnfromdb(conn):
    setconnstr.POOL.putconn(conn)


def sendtodb(
    statement, params=None, fun=None, state=None,
    isolation_level=psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
    sessid=None, return_exception=False):

    origstatement = statement
    origparams = params
    origfun = fun
    origstate = copy.deepcopy(state)

    ret = None
    exception = None

    conn = conntodb()
    conn.set_isolation_level(isolation_level)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    transaction_success = False
    abort_transaction = False
    role = 'nobody' if not sessid else \
        ('user_' + str(lib.auth.id_for_session(sessid)))
    safe_role = AsIs(role)

    try:
        cur.execute('set role %(role)s', {
            'role': safe_role})
    except psycopg2.DataError as de:
        conn.rollback()
        print(de)

        try:
            cur.execute('set role postgres', {
                'role': safe_role})
            cur.execute('create role %(role)s', {
                'role': safe_role})
            cur.execute('grant postgres to %(role)s', {
                'role': safe_role})
            cur.execute('set role %(role)s', {
                'role': safe_role})
        except Exception as exc:
            abort_transaction = True
            exception = exc
            conn.rollback()
            print(type(exc))
            print(exc)
            print(traceback.format_exc())
            traceback.print_stack()

    while not (transaction_success or abort_transaction):

        try:
            cur.execute(statement, params)
            try:
                ret = cur.fetchall()
            except psycopg2.ProgrammingError as e:
                if 'no results to fetch' in repr(e):
                    ret = []
                else:
                    raise e
            if fun:
                (statement, params, fun, state) = fun(ret, state)
            else:
                transaction_success = True
        except psycopg2.extensions.TransactionRollbackError as tre:
            print('Rolling Back: ' + str(tre))
            disconnfromdb(conn)
            return sendtodb(origstatement, origparams, origfun,
                origstate, isolation_level, sessid,
                return_exception)
        except Exception as exc:
            abort_transaction = True
            exception = exc
            conn.rollback()
            print(statement)
            print([(k, _get_param_field(v)) for (k, v) in params.items()])
            print(type(exc))
            print(exc)
            print(traceback.format_exc())
            traceback.print_stack()

        if transaction_success:
            try:
                conn.commit()
            except psycopg2.extensions.TransactionRollbackError as tre:
                disconnfromdb(conn)
                return sendtodb(origstatement, origparams, origfun,
                    origstate, isolation_level, sessid,
                    return_exception)

    disconnfromdb(conn)

    return (ret, exception) if return_exception else ret


def _get_param_field(f):
    return f if isinstance(f, str) else f.adapted


def AsIs(v):
    return psycopg2.extensions.AsIs(v)


def cur2json(cur):
    return json.dumps([dict(x) for x in cur])
