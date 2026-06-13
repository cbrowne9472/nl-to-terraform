from backend.agents.validation_agent import validate_and_fix
from backend.config import settings

VALID_TERRAFORM = """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
"""

# "cidr_blocks" is not a valid aws_vpc argument (should be "cidr_block")
BROKEN_TERRAFORM = """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_blocks = "10.0.0.0/16"
}
"""


def test_valid_terraform_passes_on_first_attempt():
    result = validate_and_fix(VALID_TERRAFORM, settings.terraform_workspace_dir, max_attempts=3)

    assert result["valid"] is True
    assert result["attempts"] == 1
    assert result["error"] is None


def test_broken_terraform_gets_fixed():
    result = validate_and_fix(BROKEN_TERRAFORM, settings.terraform_workspace_dir, max_attempts=3)

    assert result["valid"] is True
    assert result["attempts"] > 1
    assert "cidr_block" in result["code"]


def test_exhausts_attempts_and_reports_error():
    result = validate_and_fix(BROKEN_TERRAFORM, settings.terraform_workspace_dir, max_attempts=1)

    assert result["valid"] is False
    assert result["attempts"] == 1
    assert result["error"]
