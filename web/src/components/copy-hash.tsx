"use client";

import { useState } from "react";

export function CopyHash({ value }: { value?: string }) {
  const [status, setStatus] = useState<{ value: string; copied: boolean }>();
  const current = value && status?.value === value ? status : undefined;

  async function copy() {
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setStatus({ value, copied: true });
    } catch {
      setStatus({ value, copied: false });
    }
  }

  return <div className="hash-field">
    <div className="hash-toolbar">
      <code className="hash" title={value}>{value || "No verification recorded"}</code>
      <button className="button" type="button" disabled={!value} onClick={copy}>
        {current?.copied ? "Copied" : "Copy full hash"}
      </button>
    </div>
    <p className="supporting-text" role="status">
      {current ? current.copied ? "Full SHA-256 copied." : "Copy failed. Open the full hash below and copy it manually." : ""}
    </p>
    {value && <details className="full-hash"><summary>Show full diff hash</summary><code>{value}</code></details>}
  </div>;
}
