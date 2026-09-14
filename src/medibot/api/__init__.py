"""HTTP route handlers (application layer).

Route handlers must stay thin: parse request → call a service → format
response.  No business logic here.  Dependency direction is
api → services → models/schemas/core.
"""

from medibot.api.analytics import router as analytics_router
from medibot.api.chat import router as chat_router
from medibot.api.health import router as health_router
from medibot.api.memory import router as memory_router

__all__ = ["analytics_router", "chat_router", "health_router", "memory_router"]
