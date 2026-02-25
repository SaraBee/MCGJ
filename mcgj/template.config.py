# Mandatory: set `DATABASE` to the location where you would like the database
# to be.  The `init` command will create the database here, and the application
# will load it from here.
DATABASE = "/path/to/MCGJ/mcgj.db"

# You'll probably want `ENABLE_PROXYFIX` to be `True` for production since
# you'll be using a reverse proxy, and `False` for local dev instance
ENABLE_PROXYFIX = True

# Set this to any secret string you want; it's used for session cookies.
SECRET_KEY = "sekrit-key"
