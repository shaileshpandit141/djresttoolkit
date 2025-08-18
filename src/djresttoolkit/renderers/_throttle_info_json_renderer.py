from typing import Any, Mapping

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from ..throttling import ThrottleInspector


class ThrottleInfoJSONRenderer(JSONRenderer):
    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: Mapping[str, Any] | None = None,
    ) -> Any:
        """Handle throttle info to headers."""
        if renderer_context:
            response: Response | None = renderer_context.get("response")
            view = renderer_context.get("view")
            if response and view:
                # Attach throttle info to headers
                inspector = ThrottleInspector(view)
                throttle_info = inspector.get_details()
                inspector.attach_headers(
                    response=response,
                    throttle_info=throttle_info,
                )
        # Retuen Final rendered payload
        return super().render(
            data,
            accepted_media_type,
            renderer_context,
        )
