import logging
from colorlog import ColoredFormatter
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Set log level from environment variable, default to INFO if not set
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # Ensures the log level is uppercase

# Log format for console output
LOGFORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"

# Create the logger
log = logging.getLogger('PyMigrate')

# Set the logger's overall level to DEBUG so it captures everything (handlers will filter)
log.setLevel(logging.DEBUG)

# Create a colored formatter for console output
formatter = ColoredFormatter(LOGFORMAT)

# Create a stream handler for logging to the console (INFO level)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(LOG_LEVEL)  # Stream logs at the level set by environment
stream_handler.setFormatter(formatter)

# Create a file handler for logging to a file (DEBUG level)
file_handler = logging.FileHandler('logfile.log')  # Log file name
file_handler.setLevel(logging.DEBUG)  # File logs everything from DEBUG and above
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add both handlers to the logger
log.addHandler(stream_handler)
log.addHandler(file_handler)
