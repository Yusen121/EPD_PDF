import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


WORK_DIR = os.path.dirname(__file__)

# Create a custom logger
logger = logging.getLogger(__name__)

# Set the overall logging level
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()

# Set up a timed rotating file handler that creates a new log file every day
log_filename = os.path.join(WORK_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")
f_handler = TimedRotatingFileHandler(
    log_filename,
    when="midnight",
    interval=1,
    backupCount=30  # Keeps the last 30 log files; you can adjust this as needed
)

# Set levels for handlers
c_handler.setLevel(logging.ERROR)
f_handler.setLevel(logging.ERROR)

# Create formatters and add them to the handlers
c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

# Log messages
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')


# import logging
# import os
#
# WORK_DIR = os.path.dirname(__file__)
#
# # Create a custom logger
# logger = logging.getLogger(__name__)
#
# # Set the overall logging level
# logger.setLevel(logging.DEBUG)
#
# # Create handlers
# c_handler = logging.StreamHandler()
# f_handler = logging.FileHandler(os.path.join(WORK_DIR, "main.log"))
#
# # Set levels for handlers
# c_handler.setLevel(logging.INFO)
# f_handler.setLevel(logging.INFO)
#
# # Create formatters and add them to the handlers
# c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
#
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)
#
# # Add handlers to the logger
# logger.addHandler(c_handler)
# logger.addHandler(f_handler)
#
# # Log messages
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')
