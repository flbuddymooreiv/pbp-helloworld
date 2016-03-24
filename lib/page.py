def make(page, auth=False):

    return ('''
        <!doctype html>
        <html>

            <head>
                <title>Hello World</title>
                <script src="/static/jquery/jquery-1.11.0.min.js"></script>
                <script src="/static/js/longpollmux.js"></script>
                <script src="/static/js/listen.js"></script>
            </head>

            <body>
                ''' + page + '''
            </body>

        </html>
    ''')
