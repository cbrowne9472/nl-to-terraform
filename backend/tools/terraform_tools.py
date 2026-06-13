import subprocess


def run_terraform_init(workspace_dir: str) -> dict:
    result = subprocess.run(
        ["terraform", "init", "-no-color"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=120
    )
    return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}


def run_terraform_validate(workspace_dir: str) -> dict:
    result = subprocess.run(
        ["terraform", "validate", "-no-color"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )
    return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
