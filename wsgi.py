import sys
path = '/home/yourusername/mysite'
if path not in sys.path:
   sys.path.insert(0, path)

from flask_app import app as application

from mcgj import create_app
application = create_app()