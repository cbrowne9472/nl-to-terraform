import json
from typing import Optional

import boto3

# The AWS Pricing API is only available in us-east-1 and ap-south-1,
# regardless of which region the priced resources live in.
pricing_client = boto3.client("pricing", region_name="us-east-1")

REGION_MAP = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
}

# The Pricing API's databaseEngine values don't match the lowercase
# engine names used elsewhere in this project.
RDS_ENGINE_MAP = {
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
}

ALB_MONTHLY_BASE = 16.20    # fixed LCU pricing estimate
S3_PER_GB_MONTH = 0.023
ELASTICACHE_REDIS_T3_MICRO_HOURLY = 0.017
HOURS_PER_MONTH = 730


def _first_price(price_list: list) -> Optional[float]:
    if not price_list:
        return None
    price_data = json.loads(price_list[0])
    terms = price_data["terms"]["OnDemand"]
    price_dimensions = list(list(terms.values())[0]["priceDimensions"].values())
    return float(price_dimensions[0]["pricePerUnit"]["USD"])


def get_ec2_price(instance_type: str, region: str) -> Optional[float]:
    """Returns hourly on-demand Linux price in USD, or None if not found."""
    try:
        response = pricing_client.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                {"Type": "TERM_MATCH", "Field": "location", "Value": REGION_MAP.get(region, "US East (N. Virginia)")},
                {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
                {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            ],
            MaxResults=1
        )
        return _first_price(response["PriceList"])
    except Exception as e:
        print(f"Error fetching EC2 price: {e}")
        return None


def get_rds_price(instance_class: str, engine: str, region: str) -> Optional[float]:
    """Returns hourly Single-AZ on-demand price in USD, or None if not found."""
    try:
        response = pricing_client.get_products(
            ServiceCode="AmazonRDS",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_class},
                {"Type": "TERM_MATCH", "Field": "databaseEngine", "Value": RDS_ENGINE_MAP.get(engine, engine)},
                {"Type": "TERM_MATCH", "Field": "location", "Value": REGION_MAP.get(region, "US East (N. Virginia)")},
                {"Type": "TERM_MATCH", "Field": "deploymentOption", "Value": "Single-AZ"},
            ],
            MaxResults=1
        )
        return _first_price(response["PriceList"])
    except Exception as e:
        print(f"Error fetching RDS price: {e}")
        return None


def estimate_monthly_cost(resource_type: str, config: dict) -> float:
    """Returns estimated monthly cost in USD for a single resource."""
    if resource_type in ("aws_instance", "aws_launch_template"):
        hourly = get_ec2_price(config.get("instance_type", "t3.medium"), config.get("region", "us-east-1"))
        instances = config.get("instance_count", 1)
        return (hourly or 0.0416) * HOURS_PER_MONTH * instances

    elif resource_type == "aws_lb":
        return ALB_MONTHLY_BASE

    elif resource_type == "aws_db_instance":
        hourly = get_rds_price(config.get("instance_class", "db.t3.micro"),
                                config.get("engine", "postgres"),
                                config.get("region", "us-east-1"))
        return (hourly or 0.017) * HOURS_PER_MONTH

    elif resource_type == "aws_elasticache_replication_group":
        return ELASTICACHE_REDIS_T3_MICRO_HOURLY * HOURS_PER_MONTH

    elif resource_type == "aws_s3_bucket":
        return S3_PER_GB_MONTH * config.get("estimated_gb", 10)

    else:
        return 0.0  # VPCs, security groups, route tables are free
