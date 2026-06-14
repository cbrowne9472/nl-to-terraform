export default function DeployButton({ readyToDeploy, costBreakdown, onDeploy, isDeploying }) {
  const total = costBreakdown?.total_monthly_usd;

  return (
    <div className="w-full max-w-3xl mx-auto flex flex-col gap-2">
      {readyToDeploy && total != null && (
        <p className="text-sm text-gray-600">
          This will create real AWS resources estimated at{' '}
          <span className="font-semibold">${total.toFixed(2)}/month</span>. You can destroy
          everything afterwards from the deploy log.
        </p>
      )}

      <button
        onClick={onDeploy}
        disabled={!readyToDeploy || isDeploying}
        className="rounded-lg bg-green-600 px-6 py-3 font-semibold text-white hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {isDeploying ? 'Deploying…' : 'Approve & Deploy'}
      </button>
    </div>
  );
}
