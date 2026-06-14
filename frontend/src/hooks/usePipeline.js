import { useCallback, useState } from 'react';
import { startPipeline } from '../api/client';

export const PIPELINE_STAGES = ['intent', 'resources', 'terraform', 'validation', 'cost'];

const initialStages = () =>
  PIPELINE_STAGES.reduce((acc, stage) => {
    acc[stage] = { status: 'pending' };
    return acc;
  }, {});

export function usePipeline() {
  const [stages, setStages] = useState(initialStages());
  const [isRunning, setIsRunning] = useState(false);
  const [intent, setIntent] = useState(null);
  const [resources, setResources] = useState([]);
  const [terraformCode, setTerraformCode] = useState('');
  const [costBreakdown, setCostBreakdown] = useState(null);
  const [workspaceDir, setWorkspaceDir] = useState(null);
  const [readyToDeploy, setReadyToDeploy] = useState(false);
  const [error, setError] = useState(null);

  const reset = useCallback(() => {
    setStages(initialStages());
    setIntent(null);
    setResources([]);
    setTerraformCode('');
    setCostBreakdown(null);
    setWorkspaceDir(null);
    setReadyToDeploy(false);
    setError(null);
  }, []);

  const run = useCallback(async (prompt) => {
    reset();
    setIsRunning(true);

    try {
      const response = await startPipeline(prompt);

      if (!response.ok || !response.body) {
        throw new Error(`Pipeline request failed: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const messages = buffer.split('\n\n');
        buffer = messages.pop();

        for (const message of messages) {
          const line = message.split('\n').find((l) => l.startsWith('data: '));
          if (!line) continue;

          const event = JSON.parse(line.slice('data: '.length));
          const { stage, status, ...data } = event;

          if (stage === 'ready') {
            setTerraformCode(data.terraform_code);
            setWorkspaceDir(data.workspace_dir);
            setReadyToDeploy(true);
            continue;
          }

          setStages((prev) => ({ ...prev, [stage]: { status, ...data } }));

          if (stage === 'intent' && status === 'complete') setIntent(data.result);
          if (stage === 'resources' && status === 'complete') setResources(data.result);
          if (stage === 'terraform' && status === 'complete') setTerraformCode(data.code);
          if (stage === 'validation' && status === 'complete') setTerraformCode(data.code);
          if (stage === 'cost' && (status === 'complete' || status === 'blocked')) {
            setCostBreakdown(data.breakdown);
          }
          if (status === 'failed') setError(data.error);
          if (status === 'blocked') setError(data.reason);
        }
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setIsRunning(false);
    }
  }, [reset]);

  return {
    run,
    reset,
    stages,
    isRunning,
    intent,
    resources,
    terraformCode,
    costBreakdown,
    workspaceDir,
    readyToDeploy,
    error,
  };
}
