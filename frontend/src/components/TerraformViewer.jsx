import { useState } from 'react';
import Editor from '@monaco-editor/react';

const registerHcl = (monaco) => {
  if (monaco.languages.getLanguages().some((lang) => lang.id === 'hcl')) return;

  monaco.languages.register({ id: 'hcl' });
  monaco.languages.setMonarchTokensProvider('hcl', {
    keywords: ['resource', 'variable', 'provider', 'terraform', 'output', 'data', 'module', 'locals'],
    tokenizer: {
      root: [
        [/#.*$/, 'comment'],
        [/\/\/.*$/, 'comment'],
        [/"[^"]*"/, 'string'],
        [/\b(true|false|null)\b/, 'keyword'],
        [/\b\d+\b/, 'number'],
        [/\b(resource|variable|provider|terraform|output|data|module|locals)\b/, 'keyword'],
        [/[a-zA-Z_][\w-]*/, 'identifier'],
        [/[{}()\[\]]/, '@brackets'],
      ],
    },
  });
};

export default function TerraformViewer({ code }) {
  const [copied, setCopied] = useState(false);

  if (!code) return null;

  const lineCount = code.split('\n').length;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="w-full max-w-3xl mx-auto rounded-lg border border-gray-300 overflow-hidden">
      <div className="flex items-center justify-between bg-gray-50 px-4 py-2 text-sm text-gray-600">
        <span>main.tf · {lineCount} lines</span>
        <button
          onClick={handleCopy}
          className="rounded border border-gray-300 bg-white px-2 py-1 text-xs hover:bg-gray-100"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <Editor
        height="400px"
        defaultLanguage="hcl"
        value={code}
        theme="vs-dark"
        beforeMount={registerHcl}
        options={{ readOnly: true, minimap: { enabled: false }, fontSize: 13 }}
      />
    </div>
  );
}
