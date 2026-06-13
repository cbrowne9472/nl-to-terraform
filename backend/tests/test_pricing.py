import pytest
from backend.pricing.aws_pricing import get_ec2_price, get_rds_price, estimate_monthly_cost


def test_get_ec2_price_returns_positive_hourly_rate():
    price = get_ec2_price("t3.micro", "us-east-1")
    assert price is not None
    assert price > 0


def test_get_ec2_price_unknown_instance_type_returns_none():
    assert get_ec2_price("not-a-real-instance-type", "us-east-1") is None


def test_get_rds_price_returns_positive_hourly_rate():
    price = get_rds_price("db.t3.micro", "postgres", "us-east-1")
    assert price is not None
    assert price > 0


def test_get_rds_price_mysql_returns_positive_hourly_rate():
    price = get_rds_price("db.t3.micro", "mysql", "us-east-1")
    assert price is not None
    assert price > 0


def test_estimate_monthly_cost_for_ec2_instance():
    cost = estimate_monthly_cost(
        "aws_instance", {"instance_type": "t3.micro", "region": "us-east-1", "instance_count": 2}
    )
    hourly = get_ec2_price("t3.micro", "us-east-1")
    assert cost == pytest.approx(hourly * 730 * 2)


def test_estimate_monthly_cost_for_rds_instance():
    cost = estimate_monthly_cost(
        "aws_db_instance", {"instance_class": "db.t3.micro", "engine": "postgres", "region": "us-east-1"}
    )
    hourly = get_rds_price("db.t3.micro", "postgres", "us-east-1")
    assert cost == pytest.approx(hourly * 730)


def test_estimate_monthly_cost_for_alb():
    assert estimate_monthly_cost("aws_lb", {}) == 16.20


def test_estimate_monthly_cost_for_s3():
    assert estimate_monthly_cost("aws_s3_bucket", {"estimated_gb": 100}) == pytest.approx(2.3)


def test_estimate_monthly_cost_for_free_resources():
    assert estimate_monthly_cost("aws_vpc", {}) == 0.0
    assert estimate_monthly_cost("aws_subnet", {}) == 0.0
    assert estimate_monthly_cost("aws_security_group", {}) == 0.0
