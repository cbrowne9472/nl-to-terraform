import asyncio
import os
from typing import AsyncGenerator

from ..config import settings
from ..tools.terraform_tools import run_terraform_init


class InvalidWorkspaceError(Exception):
    pass


def _resolve_workspace(workspace_dir: str) -> str:
    """Ensures workspace_dir is inside the configured Terraform workspace root."""
    root = os.path.realpath(settings.terraform_workspace_dir)
    resolved = os.path.realpath(workspace_dir)
    if os.path.commonpath([root, resolved]) != root:
        raise InvalidWorkspaceError(f"{workspace_dir} is outside the Terraform workspace directory")
    return resolved


async def _stream_terraform(workspace_dir: str, label: str, *args: str) -> AsyncGenerator[str, None]:
    process = await asyncio.create_subprocess_exec(
        "terraform", *args,
        cwd=workspace_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    async for line in process.stdout:
        yield line.decode("utf-8")

    await process.wait()

    if process.returncode == 0:
        yield f"{label}_SUCCESS\n"
    else:
        yield f"{label}_FAILED: exit code {process.returncode}\n"


async def deploy(workspace_dir: str) -> AsyncGenerator[str, None]:
    """Runs terraform apply and streams output line by line."""
    try:
        workspace_dir = _resolve_workspace(workspace_dir)
    except InvalidWorkspaceError as e:
        yield f"ERROR: {e}\n"
        return

    init = run_terraform_init(workspace_dir)
    if not init["success"]:
        yield f"ERROR: terraform init failed: {init['error']}\n"
        return

    async for line in _stream_terraform(workspace_dir, "DEPLOY", "apply", "-auto-approve", "-no-color"):
        yield line


async def destroy(workspace_dir: str) -> AsyncGenerator[str, None]:
    """Runs terraform destroy and streams output line by line."""
    try:
        workspace_dir = _resolve_workspace(workspace_dir)
    except InvalidWorkspaceError as e:
        yield f"ERROR: {e}\n"
        return

    async for line in _stream_terraform(workspace_dir, "DESTROY", "destroy", "-auto-approve", "-no-color"):
        yield line
