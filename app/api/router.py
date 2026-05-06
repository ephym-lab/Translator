from fastapi import APIRouter
from app.api.routes import (
    user_routes,
    voice_routes,
    language_routes,
    tribe_routes,
    subtribe_routes,
    category_routes,
    dataset_routes,
    response_routes,
    vote_routes,
)

api_router = APIRouter()

# Auth & Users
api_router.include_router(user_routes.router)

# Reference data
api_router.include_router(language_routes.router)
api_router.include_router(tribe_routes.router)
api_router.include_router(subtribe_routes.router)
api_router.include_router(category_routes.router)

# Core platform
api_router.include_router(dataset_routes.router)
api_router.include_router(response_routes.router)
api_router.include_router(vote_routes.router)

# Voice Assistant
api_router.include_router(voice_routes.router)
