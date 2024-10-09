from datetime import datetime
import pytz


def get_utc_now():
    return datetime.now(pytz.UTC)


def get_kst_now():
    return datetime.now(pytz.timezone('Asia/Seoul'))


def convert_to_utc(dt, timezone):
    local = pytz.timezone(timezone)
    local_dt = local.localize(dt, is_dst=None)
    return local_dt.astimezone(pytz.UTC)


def convert_to_local(utc_dt, timezone):
    local = pytz.timezone(timezone)
    return utc_dt.astimezone(local)


def format_datetime(dt):
    return dt.isoformat()
