from datetime import datetime, timedelta, timezone

def format_timestamp(timestamp):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def calculate_weights(interaction_data):
    return sum(interaction.get("latency", 0) for interaction in interaction_data)

def get_gap_time_str(start_time, end_time):
    gap_time_seconds = (end_time - start_time) / 1_000_000
    gap_time_minutes = gap_time_seconds // 60
    gap_time_seconds = gap_time_seconds % 60
    gap_time_hours = 0
    if gap_time_minutes >= 120:
        gap_time_hours = gap_time_minutes // 60
        gap_time_minutes = gap_time_minutes % 60

    if gap_time_hours > 24 * 7:
        raise ValueError(f"Time range is too large. Maximum time range is 7 days. Received around {int(gap_time_hours // 24)} days.")

    if gap_time_hours == 0:
        gap_time = f"{int(gap_time_minutes)} minutes and {int(gap_time_seconds)} seconds"
    else:
        gap_time = f"{int(gap_time_hours)} hours, {int(gap_time_minutes)} minutes and {int(gap_time_seconds)} seconds"
    return gap_time

def validate_microsecond_timestamp(start_time):
    """Validate whether start_time is correctly formatted in microseconds."""

    # Convert start_time directly to a human-readable date
    converted_start_time = datetime.fromtimestamp(start_time / 1_000_000, tz=timezone.utc)

    days = start_time // (24 * 3600 * 1_000_000)
    hours = (start_time % (24 * 3600 * 1_000_000)) // (3600 * 1_000_000)
    minutes = (start_time % (3600 * 1_000_000)) // (60 * 1_000_000)
    remaining_seconds = (start_time % (60 * 1_000_000)) // 1_000_000
    microseconds = start_time % 1_000_000 

    epoch_start = datetime(1970, 1, 1, tzinfo=timezone.utc)
    print(f"Epoch start: {epoch_start}")
    constructed_start_time = epoch_start + timedelta(
        days=days, hours=hours, minutes=minutes, seconds=remaining_seconds, microseconds=microseconds
    )

    print(f"Converted start_time: {converted_start_time}")
    print(f"Constructed start_time: {constructed_start_time}")
    print(f"difference: {constructed_start_time - converted_start_time}")
    print(f"is difference greater than 5 seconds {(constructed_start_time - converted_start_time).total_seconds() > 5}")

    return (constructed_start_time - converted_start_time).total_seconds() < 5