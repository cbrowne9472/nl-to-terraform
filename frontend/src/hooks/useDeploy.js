import { useCallback, useState } from 'react';
import { deployInfrastructure, destroyInfrastructure } from '../api/client';

export function useDeploy() {
  const [logLines, setLogLines] = useState([]);
  const [status, setStatus] = useState('idle'); // idle | deploying | deployed | destroying | destroyed | failed

  const streamTo = useCallback(async (fetcher, workspaceDir, runningStatus, successStatus) => {
    setLogLines([]);
    setStatus(runningStatus);

    try {
      const response = await fetcher(workspaceDir);
      if (!response.ok || !response.body) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let failed = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.includes('FAILED') || line.startsWith('ERROR:')) failed = true;
          setLogLines((prev) => [...prev, line]);
        }
      }

      if (buffer) setLogLines((prev) => [...prev, buffer]);
      setStatus(failed ? 'failed' : successStatus);
    } catch (e) {
      setLogLines((prev) => [...prev, `ERROR: ${e.message}`]);
      setStatus('failed');
    }
  }, []);

  const deploy = useCallback(
    (workspaceDir) => streamTo(deployInfrastructure, workspaceDir, 'deploying', 'deployed'),
    [streamTo]
  );

  const destroy = useCallback(
    (workspaceDir) => streamTo(destroyInfrastructure, workspaceDir, 'destroying', 'destroyed'),
    [streamTo]
  );

  return { logLines, status, deploy, destroy };
}
