"""Utility functions for data processing."""

import datetime


def round(dt: datetime.datetime) -> datetime.datetime:
    """Round datetime to nearest 5 minutes.
    
    Args:
        dt: Datetime object to round.
        
    Returns:
        Rounded datetime object with no timezone information.
    """
    new_minute = dt.minute - dt.minute % 5
    return dt.replace(minute=new_minute, second=0, microsecond=0) 