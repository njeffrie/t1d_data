import datetime

# Round datetime value to the nearest 5 minute boundary.
def round(dt):
    new_minute = dt.minute - dt.minute % 5
    return dt.replace(minute=new_minute, second=0).isoformat()
