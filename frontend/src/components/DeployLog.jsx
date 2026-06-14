import { useEffect, useRef } from 'react';

function lineColor(line) {
  if (line.includes('FAILED') || line.startsWith('ERROR:') || /error/i.test(line)) return 'text-red-400';
  if (/creating|created|destroying|destroyed/i.test(line)) return 'text-green-400';
  if (/modifying|modified/i.test(line)) return 'text-yellow-400';
  if (line.includes('SUCCESS')) return 'text-green-400 font-semibold';
  return 'text-gray-300';
}

export default function DeployLog({ logLines, status, onDestroy }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logLines]);

  if (logLines.length === 0 && status === 'idle') return null;

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col gap-2">
      <div className="rounded-lg bg-black p-4 font-mono text-xs h-64 overflow-y-auto">
        {logLines.map((line, i) => (
          <div key={i} className={lineColor(line)}>
            {line || ' '}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {status === 'deployed' && (
        <button
          onClick={onDestroy}
          className="self-start rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
        >
          Destroy Infrastructure
        </button>
      )}
    </div>
  );
}
