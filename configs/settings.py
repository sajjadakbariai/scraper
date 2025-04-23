# configs/settings.py
from pydantic import BaseSettings, validator
from dotenv import load_dotenv
from typing import List, Optional
import logging
import os
import secrets  # For generating dummy secrets

# Define Settings class
class Settings(BaseSettings):
    """
    Configuration settings for the keyword suggestion system.
    """
    app_name: str = "Keyword Suggestion System"
    version: str = "1.0.0"
    domain_name: str = "seokar.click"
    api_domain: str = "api.seokar.click"
    api_port: int = 8000
    # Updated default database URL for PostgreSQL
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/keywords")
    telegram_bot_token: Optional[str] = None
    scraper_api_key: Optional[str] = None
    debug: bool = False
    allowed_origins: List[str] = ["*"]  # Development - Allow all origins
    allowed_origins_production: List[str] = ["https://seokar.click", "https://api.seokar.click"]  # Production - Specific origins
    env: str = os.getenv("ENV", "development")  # "development" or "production"
    keyword_scraper_api_url: Optional[str] = None
    keyword_suggestions_api_url: Optional[str] = None
    trends_api_url: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

    @validator("telegram_bot_token", "scraper_api_key")
    def sensitive_values_must_be_set_in_production(cls, v, values, field):
        if values.get("env") == "production" and not v:
            raise ValueError(f"{field.name} must be set in production environment")
        return v

    @validator("keyword_scraper_api_url", "keyword_suggestions_api_url", "trends_api_url", always=True)
    def set_api_urls(cls, v, values):
        api_domain = values.get("api_domain")
        if api_domain:
            return {
                "keyword_scraper_api_url": f"https://{api_domain}/keyword-scraper",
                "keyword_suggestions_api_url": f"https://{api_domain}/keyword-suggestions",
                "trends_api_url": f"https://{api_domain}/keyword-trends",
            }[values.field_name]
        return v


settings = None
logger = logging.getLogger(__name__)

class SensitiveDataFilter(logging.Filter):
    """
    A logging filter that masks sensitive data in messages and arguments.
    """
    def filter(self, record):
        message = record.getMessage()
        if settings:
            message = message.replace(str(settings.telegram_bot_token) if settings.telegram_bot_token else "", "***TELEGRAM_BOT_TOKEN***")
            message = message.replace(str(settings.scraper_api_key) if settings.scraper_api_key else "", "***SCRAPER_API_KEY***")

            if record.args:
                new_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        arg = arg.replace(str(settings.telegram_bot_token) if settings.telegram_bot_token else "", "***TELEGRAM_BOT_TOKEN***")
                        arg = arg.replace(str(settings.scraper_api_key) if settings.scraper_api_key else "", "***SCRAPER_API_KEY***")
                    new_args.append(arg)
                record.args = tuple(new_args)  # record.args must be a tuple

        record.msg = message
        return True


def load_settings():
    """Loads settings from environment variables and .env file."""
    global settings

    # Determine environment file
    env_file = ".env.production" if os.getenv("ENV") == "production" else ".env.development"
    load_dotenv(env_file)

    try:
        settings = Settings()
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise e

    # Configure logging level based on environment
    log_level = logging.DEBUG if settings.env == "development" else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Add sensitive data filter to logger
    logger.addFilter(SensitiveDataFilter())

    # Log loaded settings (excluding sensitive values)
    logger.info(f"App Name: {settings.app_name}")
    logger.info(f"Version: {settings.version}")
    logger.info(f"Domain Name: {settings.domain_name}")
    logger.info(f"API Domain: {settings.api_domain}")
    logger.info(f"API Port: {settings.api_port}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Allowed Origins: {settings.allowed_origins}")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Keyword Scraper API URL: {settings.keyword_scraper_api_url}")
    logger.info(f"Keyword Suggestions API URL: {settings.keyword_suggestions_api_url}")
    logger.info(f"Trends API URL: {settings.trends_api_url}")

    # For production, make sure sensitive values are set
    if settings.env == "production":
        if not settings.telegram_bot_token:
            logger.error("Telegram bot token is missing in production. Ensure TELEGRAM_BOT_TOKEN is set in .env.production.")
        if not settings.scraper_api_key:
            logger.error("Scraper API key is missing in production. Ensure SCRAPER_API_KEY is set in .env.production.")

    return settings


# Load settings when the module is imported
settings = load_settings()


if __name__ == "__main__":
    # Example usage (optional)
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.version}")
    print(f"Debug: {settings.debug}")
    print(f"Domain Name: {settings.domain_name}")
    print(f"API Domain: {settings.api_domain}")
    print(f"Keyword Scraper API URL: {settings.keyword_scraper_api_url}")
    print(f"Keyword Suggestions API URL: {settings.keyword_suggestions_api_url}")
    print(f"Trends API URL: {settings.trends_api_url}")
