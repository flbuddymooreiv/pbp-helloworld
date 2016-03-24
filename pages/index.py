import lib.page


def get(bottle):
    return lib.page.make('''
        <h1>Hello, World</h1>
        <script src="/static/js/index.js"></script>
    ''')
