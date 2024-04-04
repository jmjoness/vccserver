# import os
import logging
from app import create_app

app = create_app('development')

# desktop
if app.config['DEBUG']:
	if __name__ == '__main__':
		logging.basicConfig(filename='record.log', level=logging.DEBUG)
		app.run(host='0.0.0.0', port=5000)

# linux
# else:
# 	if __name__ == '__main__':
# 		gunicorn_logger = logging.getLogger('gunicorn.error')
# 		app.logger.handlers = gunicorn_logger.handlers
# 		app.logger.setLevel(gunicorn_logger.level)
# 		print("after app logger (linux)", flush=True)
# 		app.run()

