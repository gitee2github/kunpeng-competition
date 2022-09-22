import croniter
import datetime
import pytz
from oslo_utils import timeutils


def get_next(pattern, start_time=None, timezone="UTC"):
    """
    Get next execution time with cron pattern and start time, timezone info.
    timezone info is bound with pattern.
    :param pattern: string, Cron pattern
    :param start_time: datetime object, must be utc time
           Initial time to evaluate next executing.
    :param timezone: string, timezone info
    :return: next_time: datetime object, next executing time from start_time
             in utc time
    """
    tz = pytz.timezone(timezone)
    start_time = start_time or timeutils.utcnow(with_timezone=True)
    start_time = start_time.astimezone(tz)
    c = croniter.croniter(pattern, start_time)
    next_time = c.get_next(datetime.datetime)
    next_time = next_time.astimezone(pytz.utc)
    return next_time
