import { useState } from 'react';

const EXAMPLE_PROMPTS = [
  'highly available web app with auto scaling',
  'web app with PostgreSQL database',
  'static website with S3 and CloudFront',
  'Redis cache cluster with automatic failover',
];

export default function InputPanel({ onSubmit, isRunning }) {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || isRunning) return;
    onSubmit(prompt.trim());
  };

  const handleChipClick = (example) => {
    if (isRunning) return;
    setPrompt(example);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <textarea
          className="w-full rounded-lg border border-gray-300 p-4 text-base focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows={3}
          placeholder="Describe the infrastructure you want, e.g. 'highly available web app with auto scaling'"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={isRunning}
        />

        <div className="flex flex-wrap gap-2">
          {EXAMPLE_PROMPTS.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => handleChipClick(example)}
              disabled={isRunning}
              className="rounded-full border border-gray-300 bg-gray-50 px-3 py-1 text-sm text-gray-700 hover:bg-gray-100 disabled:opacity-50"
            >
              {example}
            </button>
          ))}
        </div>

        <button
          type="submit"
          disabled={isRunning || !prompt.trim()}
          className="self-start rounded-lg bg-blue-600 px-6 py-2 font-medium text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {isRunning ? 'Generating…' : 'Generate Infrastructure'}
        </button>
      </form>
    </div>
  );
}
