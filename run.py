#!/bin/env python
from main import create_app, socketio
import cf_deployment_tracker
import os

app = create_app(debug=True)
cf_deployment_tracker.track()
port = int(os.getenv('PORT', 8080))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port)
