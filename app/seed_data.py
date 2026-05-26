import asyncio
import os
import sys
import uuid

# Add the project root (parent directory of 'app') to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Manually load .env from the project root if it exists
env_path = os.path.join(project_root, ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                val = val.strip().strip("'\"")
                os.environ[key.strip()] = val

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.language import Language
from app.utils.logger import get_logger

logger = get_logger("seed_languages")

LANGUAGES_TO_SEED = [
    {"name": "English", "code": "eng_Latn"},
    {"name": "Swahili", "code": "swh_Latn"},
    {"name": "Kikuyu", "code": "kik_Latn"},
    {"name": "German", "code": "deu_Latn"},
    {"name": "French", "code": "fra_Latn"},
    {"name": "Russian", "code": "rus_Cyrl"},
    {"name": "Spanish", "code": "spa_Latn"},
    {"name": "Italian", "code": "ita_Latn"},
    {"name": "Portuguese", "code": "por_Latn"},
    {"name": "Chinese", "code": "zho_Hans"},
    {"name": "Japanese", "code": "jpn_Jpan"},
    {"name": "Korean", "code": "kor_Hang"},
    {"name": "Arabic", "code": "arb_Arab"},
]


async def seed_languages():
    logger.info("Starting to seed languages with NLLB/FLORES codes...")
    async with AsyncSessionLocal() as session:
        try:
            added_count = 0
            skipped_count = 0

            for lang_data in LANGUAGES_TO_SEED:
                # Check if the language code already exists
                stmt = select(Language).where(Language.code == lang_data["code"])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    logger.info(
                        f"Language '{lang_data['name']}' with code '{lang_data['code']}' already exists. Skipping."
                    )
                    skipped_count += 1
                else:
                    new_lang = Language(
                        id=uuid.uuid4(),
                        name=lang_data["name"],
                        code=lang_data["code"],
                        subtribe_id=None,
                    )
                    session.add(new_lang)
                    logger.info(f"Adding language: {lang_data['name']} ({lang_data['code']})")
                    added_count += 1

            if added_count > 0:
                await session.commit()
                logger.info(f"Successfully committed {added_count} new language(s) to the database.")
            else:
                logger.info("No new languages to add.")

            logger.info(f"Seeding completed. Added: {added_count}, Skipped: {skipped_count}.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error occurred during language seeding: {e}")
            raise e


if __name__ == "__main__":
    asyncio.run(seed_languages())
