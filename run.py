#!/bin/env python
import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', default='2Dshape', type=str)
    args = parser.parse_args()
    os.environ['domain'] = args.domain
    from main import create_app, socketio
    app = create_app(debug=False)
    socketio.run(app, host='0.0.0.0', port=80)
