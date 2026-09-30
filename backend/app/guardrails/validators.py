from app.schemas.chat import ChatResponse


def ensure_grounded_response(response: ChatResponse) -> ChatResponse:
    if response.scope_status == "in_scope" and not response.citations:
        response.scope_status = "insufficient_context"
        response.confidence = "low"
        response.caveats.append("The answer was downgraded because no citation was available.")
    return response
