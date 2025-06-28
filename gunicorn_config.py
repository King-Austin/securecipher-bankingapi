"""
Gunicorn configuration file for Secure Cipher Bank
"""
import multiprocessing

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Number of worker processes
# Using the recommended formula: 2 * number of CPU cores + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class - using the recommended async worker for Django
worker_class = "sync"  # Using sync worker for compatibility

# Maximum number of simultaneous clients per worker
worker_connections = 1000

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50  # Prevents all workers from restarting at the same time

# Process name
proc_name = "secure_cipher_bank"

# Timeout for worker silent for more than this many seconds
timeout = 120

# Log level
loglevel = "info"

# Access log - records incoming HTTP requests
accesslog = "-"  # Log to stdout

# Error log - records Gunicorn server errors
errorlog = "-"  # Log to stderr

# Whether to send Django output to the error log
capture_output = True

# How verbose the Gunicorn error logs should be
debug = False
