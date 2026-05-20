from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User, RoleEnum
from app.models.tribe import Tribe
from app.models.subtribe import SubTribe
from app.models.language import Language
from app.models.category import Category
from app.models.unclean_dataset import UncleanDataset
from app.models.response import Response
from app.models.response_vote import ResponseVote, VoteEnum


class AdminRepository:
    """Aggregated statistics queries for the admin dashboard."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_platform_stats(self) -> dict:
        try:
            # Users
            total_users = (
                await self.db.execute(select(func.count(User.id)))
            ).scalar() or 0

            verified_users = (
                await self.db.execute(
                    select(func.count(User.id)).where(User.is_verified.is_(True))
                )
            ).scalar() or 0

            active_users = (
                await self.db.execute(
                    select(func.count(User.id)).where(User.is_active.is_(True))
                )
            ).scalar() or 0

            admin_users = (
                await self.db.execute(
                    select(func.count(User.id)).where(User.role == RoleEnum.admin)
                )
            ).scalar() or 0

            # Tribes & Sub-tribes
            total_tribes = (
                await self.db.execute(select(func.count(Tribe.id)))
            ).scalar() or 0

            total_subtribes = (
                await self.db.execute(select(func.count(SubTribe.id)))
            ).scalar() or 0

            # Languages & Categories
            total_languages = (
                await self.db.execute(select(func.count(Language.id)))
            ).scalar() or 0

            total_categories = (
                await self.db.execute(select(func.count(Category.id)))
            ).scalar() or 0

            # Datasets
            total_datasets = (
                await self.db.execute(select(func.count(UncleanDataset.id)))
            ).scalar() or 0

            # Responses
            total_responses = (
                await self.db.execute(select(func.count(Response.id)))
            ).scalar() or 0

            accepted_responses = (
                await self.db.execute(
                    select(func.count(Response.id)).where(Response.is_accepted.is_(True))
                )
            ).scalar() or 0

            ai_responses = (
                await self.db.execute(
                    select(func.count(Response.id)).where(
                        Response.is_ai_generated.is_(True)
                    )
                )
            ).scalar() or 0

            human_responses = total_responses - ai_responses

            # Votes
            total_votes = (
                await self.db.execute(select(func.count(ResponseVote.id)))
            ).scalar() or 0

            accept_votes = (
                await self.db.execute(
                    select(func.count(ResponseVote.id)).where(
                        ResponseVote.vote == VoteEnum.accept
                    )
                )
            ).scalar() or 0

            reject_votes = (
                await self.db.execute(
                    select(func.count(ResponseVote.id)).where(
                        ResponseVote.vote == VoteEnum.reject
                    )
                )
            ).scalar() or 0

            # Derived metrics
            acceptance_rate = (
                round((accepted_responses / total_responses) * 100, 2)
                if total_responses > 0
                else 0.0
            )

            return {
                "users": {
                    "total": total_users,
                    "verified": verified_users,
                    "unverified": total_users - verified_users,
                    "active": active_users,
                    "inactive": total_users - active_users,
                    "admins": admin_users,
                    "regular": total_users - admin_users,
                },
                "tribes": {
                    "total": total_tribes,
                    "subtribes": total_subtribes,
                },
                "languages": {
                    "total": total_languages,
                },
                "categories": {
                    "total": total_categories,
                },
                "datasets": {
                    "total": total_datasets,
                },
                "responses": {
                    "total": total_responses,
                    "accepted": accepted_responses,
                    "pending": total_responses - accepted_responses,
                    "ai_generated": ai_responses,
                    "human": human_responses,
                    "acceptance_rate_percent": acceptance_rate,
                },
                "votes": {
                    "total": total_votes,
                    "accept": accept_votes,
                    "reject": reject_votes,
                },
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error: failed to fetch platform stats: {str(e)}",
            ) from e
