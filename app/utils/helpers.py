def format_timestamp(timestamp):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def calculate_weights(interaction_data):
    return sum(interaction.get("latency", 0) for interaction in interaction_data)
