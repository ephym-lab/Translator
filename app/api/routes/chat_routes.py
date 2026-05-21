import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.api_response import APIResponse
from app.schemas.pagination import PaginatedData
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatMessageResponse,
    ChatSessionWithMessages,
    SendMessageRequest,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)


#Session endpoints

@router.post(
    "/sessions",
    response_model=APIResponse[ChatSessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Start a new chat session",
    description=(
        "Opens a bilateral chat session between the current user and a recipient. "
        "Both participants declare their preferred language upfront. "
        "Returns 400 if a session already exists — use GET /sessions/with/{user_id} instead."
    ),
)
async def create_session(
    data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    result = await svc.create_session(current_user, data)
    return APIResponse(
        success=True,
        message="Chat session created successfully.",
        data=result,
        status=status.HTTP_201_CREATED,
    )


@router.get(
    "/sessions",
    response_model=APIResponse[list[ChatSessionResponse]],
    summary="List my chat sessions",
)
async def list_my_sessions(
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    """Returns all chat sessions the current user is part of."""
    result = await svc.list_my_sessions(current_user)
    return APIResponse(
        success=True,
        message="Chat sessions retrieved successfully.",
        data=result,
        status=status.HTTP_200_OK,
    )


@router.get(
    "/sessions/with/{other_user_id}",
    response_model=APIResponse[ChatSessionWithMessages],
    summary="Get or open a session with another user",
)
async def get_or_open_session(
    other_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    """
    Returns the existing session with this user (including messages), or creates
    a new one with default language preferences (both English).
    Useful for the frontend's 'Open Chat' button.
    """
    data = ChatSessionCreate(
        recipient_id=other_user_id,
        initiator_language="english",
        recipient_language="english",
    )
    session = await svc.get_or_open_session(current_user, data)
    messages, _ = await svc.get_messages(session.id, current_user, limit=50, offset=0)
    return APIResponse(
        success=True,
        message="Chat session retrieved successfully.",
        data=ChatSessionWithMessages(
            session=ChatSessionResponse.model_validate(session),
            messages=[ChatMessageResponse.model_validate(m) for m in messages],
        ),
        status=status.HTTP_200_OK,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=APIResponse[ChatSessionWithMessages],
    summary="Get a session with its messages",
)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    session = await svc.get_session(session_id, current_user)
    messages, _ = await svc.get_messages(session.id, current_user, limit=50, offset=0)
    return APIResponse(
        success=True,
        message="Chat session retrieved successfully.",
        data=ChatSessionWithMessages(
            session=ChatSessionResponse.model_validate(session),
            messages=[ChatMessageResponse.model_validate(m) for m in messages],
        ),
        status=status.HTTP_200_OK,
    )


@router.patch(
    "/sessions/{session_id}/languages",
    response_model=APIResponse[ChatSessionResponse],
    summary="Update language preferences for a session",
)
async def update_session_languages(
    session_id: uuid.UUID,
    data: ChatSessionUpdate,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    """Either participant can update the language preferences at any time."""
    result = await svc.update_session_languages(session_id, current_user, data)
    return APIResponse(
        success=True,
        message="Language preferences updated successfully.",
        data=result,
        status=status.HTTP_200_OK,
    )


@router.patch(
    "/sessions/{session_id}/close",
    response_model=APIResponse[ChatSessionResponse],
    summary="Close a chat session",
)
async def close_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    """Mark a session as closed. No further messages can be sent."""
    result = await svc.close_session(session_id, current_user)
    return APIResponse(
        success=True,
        message="Chat session closed.",
        data=result,
        status=status.HTTP_200_OK,
    )


@router.patch(
    "/sessions/{session_id}/reopen",
    response_model=APIResponse[ChatSessionResponse],
    summary="Re-open a closed chat session",
)
async def reopen_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    """Re-activate a previously closed session so messages can be sent again."""
    result = await svc.reopen_session(session_id, current_user)
    return APIResponse(
        success=True,
        message="Chat session re-opened.",
        data=result,
        status=status.HTTP_200_OK,
    )


#Message endpoints

@router.post(
    "/sessions/{session_id}/messages",
    response_model=APIResponse[ChatMessageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send a message (with auto-translation)",
    description=(
        "Send a message in your language — it will be automatically translated "
        "into the recipient's preferred language using the NLLB translation model.\n\n"
        "**Request body:**\n"
        "```json\n"
        '{"text": "uko vipi", "source_lang": "swahili", "target_lang": "english"}\n'
        "```"
    ),
)
async def send_message(
    session_id: uuid.UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    result = await svc.send_message(session_id, current_user, payload)
    return APIResponse(
        success=True,
        message="Message sent successfully.",
        data=result,
        status=status.HTTP_201_CREATED,
    )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=APIResponse[PaginatedData[ChatMessageResponse]],
    summary="Get messages for a session (paginated)",
)
async def get_messages(
    session_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    svc: ChatService = Depends(get_service),
):
    messages, total = await svc.get_messages(session_id, current_user, limit, offset)
    return APIResponse(
        success=True,
        message="Messages retrieved successfully.",
        data=PaginatedData(total=total, limit=limit, offset=offset, items=messages),
        status=status.HTTP_200_OK,
    )
