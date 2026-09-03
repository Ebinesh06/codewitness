"use client";

import { useState } from "react";

const demos = {
  rounding: { label: "Rounding behaviour", functionName: "calculate_discount", original: "def calculate_discount(price, discount):\n    return round(price * (1 - discount), 2)", generated: "def calculate_discount(price, discount):\n    return int(price * (1 - discount))" },
  boundary: { label: "Boundary behaviour", functionName: "is_eligible", original: "def is_eligible(score):\n    return score >= 50", generated: "def is_eligible(score):\n    return score > 50" },
  empty: { label: "Empty input behaviour", functionName: "get_first", original: "def get_first(items):\n    if not items:\n        return None\n    return items[0]", generated: "def get_first(items):\n    return items[0]" },
  equivalent: { label: "Equivalent refactor", functionName: "add", original: "def add(a, b):\n    return a + b", generated: "def add(a, b):\n    result = a + b\n    return result" },
};

type Result = { verdict: { status: string; message: string }; metrics: { tests_generated: number; tests_executed: number; divergences: number; execution_time_ms: number }; properties: { name: string; description: string }[]; counterexample?: { inputs: unknown[]; original: Record<string, unknown>; generated: Record<string, unknown> }; reproduced?: boolean; evidence: Record<string, unknown> };

export default function Home() {
  const [original, setOriginal] = useState(demos.boundary.original);
  const [generated, setGenerated] = useState(demos.boundary.generated);
  const [functionName, setFunctionName] = useState("is_eligible");
  const [intent, setIntent] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [rerunning, setRerunning] = useState(false);
  const [error, setError] = useState("");
  const [stage, setStage] = useState("");

  const verify = async (counterexampleInputs?: unknown[]) => {
    const isRerun = counterexampleInputs !== undefined;
    setBusy(true); setRerunning(isRerun); setError("");
    if (!isRerun) setResult(null);
    setStage("RUNNING VERIFICATION");
    try {
      const response = await fetch("http://127.0.0.1:8000/api/verify", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ original_code: original, generated_code: generated, function_name: functionName, intent: intent || null, counterexample_inputs: counterexampleInputs }) });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Verification failed");
      setResult(payload);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Verification failed"); }
    finally { setBusy(false); setRerunning(false); setStage(""); }
  };

  const loadDemo = (key: keyof typeof demos) => { const demo = demos[key]; setOriginal(demo.original); setGenerated(demo.generated); setFunctionName(demo.functionName); setResult(null); setError(""); };

  return (
    <div className="shell"><header><div className="brand-mark">CW</div><div><h1>CODE-WITNESS</h1><p>Reproducible software verification</p></div><div className="header-status"><span className="pulse" /> LOCAL ENGINE <small>v0.1</small></div></header>
      <main><section className="intro"><div><span className="eyebrow">VERIFICATION WORKSPACE / PYTHON</span><h2>Test the change.<br /><em>Trust the evidence.</em></h2></div><p className="intro-copy">Compare observable behaviour across two implementations with deterministic execution and reproducible counterexamples.</p></section>
        <section className="demo-strip"><span>LOAD REAL DEMO</span>{(Object.keys(demos) as (keyof typeof demos)[]).map((key) => <button key={key} onClick={() => loadDemo(key)}>{demos[key].label}</button>)}</section>
        <section className="editors"><Editor title="SOURCE ARTEFACT" value={original} setValue={setOriginal} /><div className="versus">VS</div><Editor title="GENERATED ARTEFACT" value={generated} setValue={setGenerated} /></section>
        <section className="controls"><label>FUNCTION NAME<input value={functionName} onChange={(event) => setFunctionName(event.target.value)} /></label><label className="intent">INTENDED BEHAVIOUR <span>(OPTIONAL)</span><input value={intent} onChange={(event) => setIntent(event.target.value)} placeholder="Describe the behaviour to preserve" /></label><button className="verify" onClick={() => verify()} disabled={busy}>{busy ? "VERIFYING..." : "VERIFY"}<span>→</span></button></section>
        {busy && <section className="pipeline"><span className="eyebrow">LIVE EXECUTION</span><div className="active"><i />{stage}</div></section>}
        {error && <div className="error">{error}</div>}
        {result && <ResultPanel result={result} rerun={verify} rerunning={rerunning} original={original} generated={generated} />}
      </main><footer><span>DETERMINISTIC EXECUTION</span><span>SUBPROCESS ISOLATION</span><span>SHA-256 EVIDENCE</span></footer>
    </div>
  );
}

function Editor({ title, value, setValue }: { title: string; value: string; setValue: (value: string) => void }) { return <div className="editor"><div className="editor-head"><span className="dot" />{title}<span className="language">PYTHON</span></div><textarea spellCheck={false} value={value} onChange={(event) => setValue(event.target.value)} /></div>; }

function ResultPanel({ result, rerun, rerunning, original, generated }: { result: Result; rerun: (inputs?: unknown[]) => void; rerunning: boolean; original: string; generated: string }) {
  const failed = result.verdict.status === "DIVERGENCE_DETECTED";
  const parameterNames = original.match(/def\s+\w+\(([^)]*)\)/)?.[1].split(",").map((name) => name.trim()).filter(Boolean) ?? [];
  const inputRows = result.counterexample?.inputs.map((value, index) => ({ name: parameterNames[index] || `argument ${index + 1}`, value }));
  const evidence = result.evidence;
  return <section className="results">
    <div className="result-head"><div><span className="eyebrow">VERIFICATION RESULT</span><h2 className={failed ? "failure" : "success"}>{failed ? "BEHAVIOURAL DIVERGENCE DETECTED" : "VERIFICATION PASSED"}</h2><p>{result.verdict.message}</p></div><div className="status-badge"><span className="pulse" />{result.verdict.status.replaceAll("_", " ")}</div></div>
    <div className="metrics">{[["TESTS EXECUTED", result.metrics.tests_executed], ["PROPERTIES CHECKED", result.properties.length], ["DIVERGENCES", result.metrics.divergences], ["EXECUTION TIME", `${result.metrics.execution_time_ms} ms`]].map(([label, value]) => <div key={String(label)}><span>{label}</span><strong>{value}</strong></div>)}</div>
    {result.counterexample && <div className="finding"><span className="eyebrow">MINIMAL COUNTEREXAMPLE</span><div className="input-list">{inputRows?.map((row) => <div key={row.name}><span>{row.name}</span><strong>{String(row.value)}</strong></div>)}</div><div className="outputs"><div><span>ORIGINAL RESULT</span><strong>{formatResult(result.counterexample.original)}</strong></div><div><span>GENERATED RESULT</span><strong>{formatResult(result.counterexample.generated)}</strong></div></div><button className="rerun" onClick={() => rerun(result.counterexample?.inputs)} disabled={rerunning}>{rerunning ? "RE-RUNNING..." : "↻ RE-RUN COUNTEREXAMPLE"}</button>{result.reproduced !== undefined && <div className={`reproduction ${result.reproduced ? "confirmed" : "not-confirmed"}`}><span className="eyebrow">REPRODUCTION CHECK</span><strong>{result.reproduced ? "✓ COUNTEREXAMPLE REPRODUCED" : "! COUNTEREXAMPLE NOT REPRODUCED"}</strong></div>}</div>}
    <div className="contract"><h3>BEHAVIOURAL CONTRACT</h3>{result.properties.map((property) => <div className="contract-row" key={property.name}><span>•</span><strong>{property.name}</strong></div>)}</div>
    <details className="evidence"><summary>EVIDENCE</summary><div className="evidence-summary"><div><span>Source SHA-256</span><code>{String(evidence.source_hash)}</code></div><div><span>Generated SHA-256</span><code>{String(evidence.generated_hash)}</code></div><div><span>Test seed</span><code>{String(evidence.test_seed)}</code></div><div><span>Tests executed</span><code>{String(evidence.tests_executed)}</code></div><div><span>Execution environment</span><code>{String((evidence.execution_environment as { python?: string })?.python)}</code></div></div><details className="execution-details"><summary>VIEW FULL EVIDENCE</summary><pre>{JSON.stringify(evidence, null, 2)}</pre><pre className="diff">{original.split("\n").map((line) => `- ${line}`).join("\n")}\n{generated.split("\n").map((line) => `+ ${line}`).join("\n")}</pre></details></details>
  </section>;
}

function formatResult(execution: Record<string, unknown>) { if (execution.exception) { const exception = execution.exception as { type?: string; message?: string }; return `${exception.type}: ${exception.message}`; } return `${String(execution.value)} (${String(execution.type)})`; }
