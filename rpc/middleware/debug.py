from django.conf import settings
from django.db import connection
import json
import time


class APIDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not settings.DEBUG
            or not request.path.startswith("/api/")
            or not request.GET.get("debug")
        ):
            return self.get_response(request)

        # Start profiling
        start_time = time.time()
        initial_queries = len(connection.queries)

        response = self.get_response(request)

        # Calculate profiling metrics
        end_time = time.time()
        final_queries = len(connection.queries)
        query_count = final_queries - initial_queries
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Only wrap JSON API responses
        if "application/json" in response.get("Content-Type", "") and hasattr(
            response, "content"
        ):
            try:
                # Parse existing JSON response
                original_data = json.loads(response.content.decode("utf-8"))

                # Calculate query timing
                query_time = (
                    sum(float(q["time"]) for q in connection.queries[initial_queries:])
                    * 1000
                )

                # Wrap with debug info
                wrapped_data = {
                    "_debug": {
                        "query_count": query_count,
                        "query_time_ms": round(query_time, 2),
                        "total_time_ms": round(total_time, 2),
                        "queries": [
                            {"sql": q["sql"], "time_ms": float(q["time"]) * 1000}
                            for q in connection.queries[initial_queries:]
                        ]
                        if query_count <= 200
                        else f"Too many queries ({query_count}) - not showing details",
                    },
                    "data": original_data,
                }

                # Update response content
                response.content = json.dumps(wrapped_data, indent=2).encode("utf-8")
                response["Content-Length"] = str(len(response.content))

            except (json.JSONDecodeError, UnicodeDecodeError):
                # If we can't parse the JSON, just add headers
                response["X-Debug-Query-Count"] = str(query_count)
                response["X-Debug-Total-Time"] = f"{total_time:.2f}ms"

        return response
