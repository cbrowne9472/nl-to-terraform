from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from . import llm, tracer

RESOURCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AWS infrastructure expert. Given infrastructure requirements,
    return the exact list of Terraform resources needed.

    Rules:
    - Always include VPC, subnets, internet gateway, and route tables for any web workload
    - Multi-AZ means at least 2 subnets in different availability zones
    - Load balanced means ALB + target group + listener + security group for ALB
    - Auto scaling means launch template + autoscaling group + scaling policies
    - Always include security groups for every compute resource
    - Never include resources that are not needed
    - Maximum {max_resources} resources total

    Return JSON with key "resources": array of objects with fields:
    - resource_type: the Terraform resource type (e.g. aws_vpc)
    - name: the logical name (e.g. main)
    - description: one sentence explaining why this resource is needed
    - snippet_key: which template to use (vpc|ec2|alb|asg|rds|elasticache|s3|security_group)

    Each snippet template contains specific Terraform resource types, and every
    resource_type value you return MUST be one of the types listed below for its
    snippet_key (case-sensitive, no other resource types exist):
    - vpc: aws_vpc, aws_subnet, aws_internet_gateway, aws_route_table, aws_route_table_association
    - ec2: aws_instance
    - alb: aws_lb, aws_lb_target_group, aws_lb_listener
    - asg: aws_launch_template, aws_autoscaling_group, aws_autoscaling_policy
    - rds: aws_db_subnet_group, aws_security_group, aws_db_instance
    - elasticache: aws_elasticache_subnet_group, aws_security_group, aws_elasticache_replication_group
    - s3: aws_s3_bucket, aws_s3_bucket_versioning, aws_s3_bucket_server_side_encryption_configuration, aws_s3_bucket_public_access_block
    - security_group: aws_security_group

    Note: there is no standalone "aws_route" resource — route tables are
    represented by aws_route_table and aws_route_table_association.
    """),
    ("human", "Plan resources for this intent: {intent}")
])


def plan_resources(intent: dict, max_resources: int = 20) -> list:
    chain = RESOURCE_PROMPT | llm | JsonOutputParser()
    result = chain.invoke(
        {"intent": str(intent), "max_resources": max_resources},
        config={"callbacks": [tracer], "run_name": "resource-planning"}
    )
    return result.get("resources", [])
