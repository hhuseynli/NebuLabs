from slowapi import Limiter
from slowapi.util import get_remote_address


# Shared limiter used by AI-heavy endpoints to prevent abuse and quota spikes.
limiter = Limiter(key_func=get_remote_address)
