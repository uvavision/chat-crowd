#!/bin/env python
from main import create_app, socketio
import os

app = create_app(debug=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
