# Import all models here so Alembic's autogenerate can discover them.
from app.models.language import Language           # noqa: F401
from app.models.tribe import Tribe                  # noqa: F401
from app.models.subtribe import SubTribe            # noqa: F401
from app.models.category import Category            # noqa: F401
from app.models.otp import OTP                      # noqa: F401
from app.models.user import User, GenderEnum, RoleEnum  # noqa: F401
from app.models.user_language import UserLanguage   # noqa: F401
from app.models.refresh_token import RefreshToken   # noqa: F401
from app.models.unclean_dataset import UncleanDataset, DatasetLevelEnum  # noqa: F401
from app.models.response import Response            # noqa: F401
from app.models.response_vote import ResponseVote, VoteEnum  # noqa: F401

