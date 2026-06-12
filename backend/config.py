from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    langchain_api_key: str
    langchain_project: str = "nl-to-terraform"
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str = "us-east-1"
    max_terraform_resources: int = 20
    max_monthly_cost_usd: float = 500.0
    terraform_workspace_dir: str = "./backend/terraform/workspace"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
