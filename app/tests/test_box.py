
# This is mearly a script I can run by itself to test out code.

from datetime import datetime, timezone
#from app.utils.utils import format_json_string

now = datetime.now(timezone.utc)   # gives the current time in your timezone.. apparently 
                       # But if previously using utcnow() if fucks everyting up... so use
                       # .now(timezone.utc)?? 
print(now)