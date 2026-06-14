const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const startPipeline = async (prompt) => {
  return fetch(`${BASE_URL}/pipeline/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
};

export const deployInfrastructure = async (workspaceDir) => {
  return fetch(
    `${BASE_URL}/pipeline/deploy?workspace_dir=${encodeURIComponent(workspaceDir)}`,
    { method: 'POST' }
  );
};

export const destroyInfrastructure = async (workspaceDir) => {
  return fetch(
    `${BASE_URL}/pipeline/destroy?workspace_dir=${encodeURIComponent(workspaceDir)}`,
    { method: 'POST' }
  );
};
