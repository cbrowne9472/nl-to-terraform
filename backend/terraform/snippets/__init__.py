import os

SNIPPET_DIR = os.path.dirname(__file__)

SNIPPET_FILES = {
    "vpc": "vpc.tf.tmpl",
    "ec2": "ec2.tf.tmpl",
    "alb": "alb.tf.tmpl",
    "asg": "asg.tf.tmpl",
    "rds": "rds.tf.tmpl",
    "elasticache": "elasticache.tf.tmpl",
    "s3": "s3.tf.tmpl",
    "security_group": "security_groups.tf.tmpl",
}


def load_snippet(key: str) -> str:
    """Reads and returns the raw Terraform template content for a snippet key."""
    filename = SNIPPET_FILES.get(key)
    if filename is None:
        raise KeyError(f"Unknown snippet key: {key}")

    path = os.path.join(SNIPPET_DIR, filename)
    with open(path) as f:
        return f.read()
