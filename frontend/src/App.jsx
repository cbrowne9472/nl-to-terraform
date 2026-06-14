import InputPanel from './components/InputPanel';
import AgentProgress from './components/AgentProgress';
import TerraformViewer from './components/TerraformViewer';
import CostBreakdown from './components/CostBreakdown';
import DeployButton from './components/DeployButton';
import DeployLog from './components/DeployLog';
import { usePipeline } from './hooks/usePipeline';
import { useDeploy } from './hooks/useDeploy';

export default function App() {
  const pipeline = usePipeline();
  const deployment = useDeploy();

  const hasStarted = Object.values(pipeline.stages).some((s) => s.status !== 'pending');

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-4">
      <div className="max-w-3xl mx-auto mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">NL to Terraform</h1>
        <p className="text-gray-600 mt-2">
          Describe the AWS infrastructure you need in plain English.
        </p>
      </div>

      <div className="flex flex-col gap-6">
        <InputPanel onSubmit={pipeline.run} isRunning={pipeline.isRunning} />

        {hasStarted && <AgentProgress stages={pipeline.stages} />}

        {pipeline.error && (
          <div className="w-full max-w-3xl mx-auto rounded-lg border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
            {pipeline.error}
          </div>
        )}

        <TerraformViewer code={pipeline.terraformCode} />

        <CostBreakdown breakdown={pipeline.costBreakdown} />

        {pipeline.readyToDeploy && (
          <DeployButton
            readyToDeploy={pipeline.readyToDeploy}
            costBreakdown={pipeline.costBreakdown}
            isDeploying={deployment.status === 'deploying'}
            onDeploy={() => deployment.deploy(pipeline.workspaceDir)}
          />
        )}

        <DeployLog
          logLines={deployment.logLines}
          status={deployment.status}
          onDestroy={() => deployment.destroy(pipeline.workspaceDir)}
        />
      </div>
    </div>
  );
}
