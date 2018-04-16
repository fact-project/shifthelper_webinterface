from flask import current_app
from time import sleep
from itertools import count


def get_size(f):
    pos = f.tell()
    f.seek(0, 2)
    size = f.tell()
    f.seek(pos)
    return size


def log_generator():
    '''
    Generates the bodies of server sent events from the shifthelper log.
    To be used as streamed response use flask.Respone(log_generator()).
    Can handle logfile rotation by comparing the size of the file
    to the current position.
    '''
    with open(current_app.config['shifthelper_log']) as f:
        for i in count():
            if f.tell() > get_size(f):
                f.seek(0)
                msg = build_sse('{:*^80}'.format('file truncated '), i)
            else:
                msg = f.read()
            yield build_sse(msg, i)
            sleep(1)


def build_sse(message, id_=None):
    '''
    Create the body for a server sent event from
    data `message` and optional id `id_`
    '''
    sse = ''
    if id_ is not None:
        sse += 'id: {}\n'.format(id_)
    sse += 'data: ' + '\ndata: '.join(message.splitlines())
    sse += '\n\n'
    return sse
