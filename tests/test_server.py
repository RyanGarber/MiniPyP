from minipyp import *

# An example server
MiniPyP(host='0.0.0.0', port=80, sites=[
    {
        'uris': ['127.0.0.1', 'localhost'],
        'root': 'C:\\Users\\Ryan\\Documents\\Public',
        'paths': {
            '/api': {
                'proxy': 'http://api.triptelfler.co/2'
            }
        }
    }
], directories={
    'C:\\': {
        'public': False
    },
    'C:\\Users\\Ryan\\Documents\\Public': {
        'public': True
    }
}).start()
