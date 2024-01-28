
# event types from polygon web socket
import os
import pathlib

EVENT_TYPE_SEC = 'A'
EVENT_TYPE_MIN = 'AM'

# alert_manager
ALERT_ROOT_DIR = pathlib.Path().resolve()
ALERTS_FILE_PATH = os.path.join(ALERT_ROOT_DIR, "alerts_log_file")
EMPTY_ALERT_RECORD = 'pass'
