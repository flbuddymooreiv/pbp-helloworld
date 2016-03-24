# PUBLIC CONTENT (NOT PASSWORD PROTECTED!!!)
PUBLIC_STATIC_CONTENT = [
    {'url': 'static/jquery/jquery-1.11.0.min.js',
        'mimetype': 'text/javascript'},
    {'url': 'static/js/listen.js', 'mimetype': 'text/javascript'},
    {'url': 'static/js/longpollmux.js', 'mimetype': 'text/javascript'},
    {'url': 'static/js/index.js', 'mimetype': 'text/javascript'},
]

PUBLIC_DYNAMIC_CONTENT = [
    {'url': '', 'module': 'index'}
]

# Everyone gets Read, only Data Admins get Write
API_HANDLERS = [
    'testtype'
]
