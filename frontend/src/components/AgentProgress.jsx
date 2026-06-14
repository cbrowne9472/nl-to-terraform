import { PIPELINE_STAGES } from '../hooks/usePipeline';

const STAGE_LABELS = {
  intent: 'Extract Intent',
  resources: 'Plan Resources',
  terraform: 'Generate Terraform',
  validation: 'Validate & Self-Heal',
  cost: 'Estimate Cost',
};

const STATUS_STYLES = {
  pending: 'bg-gray-100 text-gray-400 border-gray-200',
  running: 'bg-blue-50 text-blue-600 border-blue-300',
  complete: 'bg-green-50 text-green-700 border-green-300',
  failed: 'bg-red-50 text-red-700 border-red-300',
  blocked: 'bg-yellow-50 text-yellow-700 border-yellow-300',
};

function StatusIcon({ status }) {
  if (status === 'running') {
    return (
      <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-blue-300 border-t-blue-600" />
    );
  }
  if (status === 'complete') return <span>✓</span>;
  if (status === 'failed') return <span>✕</span>;
  if (status === 'blocked') return <span>⚠</span>;
  return <span className="opacity-40">●</span>;
}

export default function AgentProgress({ stages }) {
  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col gap-2">
      {PIPELINE_STAGES.map((stage) => {
        const status = stages[stage]?.status || 'pending';
        return (
          <div
            key={stage}
            className={`flex items-center justify-between rounded-lg border px-4 py-2 text-sm font-medium ${STATUS_STYLES[status] || STATUS_STYLES.pending}`}
          >
            <span>{STAGE_LABELS[stage]}</span>
            <StatusIcon status={status} />
          </div>
        );
      })}
    </div>
  );
}
