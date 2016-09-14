from shifthelper_webinterface import app, socket

if __name__ == '__main__':
    socket.run(app, host='0.0.0.0', port=5000)
