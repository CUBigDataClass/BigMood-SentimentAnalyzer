from datetime import datetime, timedelta

# function to get current timestamp used for get endpoint query parameters
def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))