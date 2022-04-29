from datetime import datetime, timezone

print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"))