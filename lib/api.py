import urllib.parse


def query_field(query, field):
    field_spec = field in query
    return (field_spec, query[field] if field_spec else '')


def unpack_id_list(l):
    return [int(x) for x in
            [_f for _f in urllib.parse.unquote_plus(l).split(',') if _f]]
