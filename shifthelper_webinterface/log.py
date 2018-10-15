from flask import current_app
from time import sleep
from itertools import count


def get_size(f):
    pos = f.tell()
    f.seek(0, 2)
    size = f.tell()
    f.seek(pos)
    return size


def log_generator(max_size=50000):
    '''
    Generates the bodies of server sent events from the shifthelper log.
    To be used as streamed response use flask.Respone(log_generator()).
    Can handle logfile rotation by comparing the size of the file
    to the current position.
    '''
    with open(current_app.config['shifthelper_log'], 'rb') as f:
        for i in count():
            size = get_size(f)

            # truncate to max_size
            if i == 0 and size > max_size:
                f.seek(-max_size, 2)
                yield build_sse('{:*^40}'.format(
                    'Log output truncated to {} kB'.format(max_size // 1000)
                ), i)

            if f.tell() > size:
                f.seek(0)
                msg = build_sse('{:*^40}'.format(
                    'Log file was truncated, probably log rotation'
                ), i)
            else:
                msg = f.read().decode()

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
