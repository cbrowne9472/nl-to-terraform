const TIER_COLORS = {
  low: 'text-green-600',
  medium: 'text-yellow-600',
  high: 'text-red-600',
};

function totalColor(total) {
  if (total < 50) return 'text-green-600';
  if (total <= 200) return 'text-yellow-600';
  return 'text-red-600';
}

export default function CostBreakdown({ breakdown }) {
  if (!breakdown) return null;

  const { line_items = [], total_monthly_usd = 0, cost_tier, optimization_tips = [] } = breakdown;

  return (
    <div className="w-full max-w-3xl mx-auto rounded-lg border border-gray-300 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              <th className="px-4 py-2">Resource</th>
              <th className="px-4 py-2 text-right">Monthly Cost (USD)</th>
              <th className="px-4 py-2">Notes</th>
            </tr>
          </thead>
          <tbody>
            {line_items.map((item, i) => (
              <tr key={i} className="border-t border-gray-200">
                <td className="px-4 py-2 font-mono text-xs">{item.resource}</td>
                <td className="px-4 py-2 text-right">${item.monthly_cost_usd?.toFixed(2)}</td>
                <td className="px-4 py-2 text-gray-500">{item.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between border-t border-gray-200 bg-gray-50 px-4 py-3">
        <span className="font-medium">Total Monthly Cost</span>
        <span className={`text-lg font-bold ${TIER_COLORS[cost_tier] || totalColor(total_monthly_usd)}`}>
          ${total_monthly_usd?.toFixed(2)} / month
        </span>
      </div>

      {optimization_tips.length > 0 && (
        <div className="px-4 py-3 text-sm">
          <p className="font-medium text-gray-700 mb-1">Optimization tips</p>
          <ul className="list-disc list-inside space-y-1 text-gray-600">
            {optimization_tips.map((tip, i) => (
              <li key={i}>{tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
