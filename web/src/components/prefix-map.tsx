"use client";

import { useLayoutEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { tokenColor } from "@/lib/heatmap";
import { number } from "@/lib/workspace";

export function PrefixMap({ values, boundary, first, total }: {
  values: number[]; boundary: number | null; first: number | null; total?: number;
}) {
  const root = useRef<HTMLDivElement>(null);
  const [initial] = useState(() => ({ values, boundary }));
  const columns = 50, rowHeight = 10, width = 1000;
  const height = Math.ceil(values.length / columns) * rowHeight;
  useLayoutEffect(() => {
    const svg = root.current;
    if (!svg) return;
    const tokens = svg.querySelectorAll("[data-token]");
    const marker = svg.querySelector("[data-cache-marker]");
    const label = svg.querySelector("[data-cache-label]");
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    let tweens: gsap.core.Tween[] = [];
    const apply = () => {
      tweens.forEach(t => t.kill());
      const options = { duration: preference.matches ? 0 : 0.6, ease: "power3.out", overwrite: true };
      tweens = [gsap.to(tokens, { ...options, fill: (i: number) => tokenColor(values[i], i, values.length, boundary) })];
      if (boundary !== null) {
        if (marker) tweens.push(gsap.to(marker, { ...options, attr: { transform: `translate(0 ${boundary * height})` } }));
        if (label) tweens.push(gsap.to(label, { ...options, top: `${(26 + boundary * height) / (height + 52) * 100}%` }));
      }
    };
    apply();
    preference.addEventListener("change", apply);
    return () => { preference.removeEventListener("change", apply); tweens.forEach(t => t.kill()); };
  }, [values, boundary, height]);

  return <figure className="prefix-map">
    <div className="prefix-canvas" ref={root}><svg viewBox={`0 -26 ${width} ${height + 52}`} role="img"
      aria-label={`SIMULATED prefix map, read left to right then down. ${first === null ? "No divergence finding recorded." : `Earliest divergence at token ${first} of ${total ?? "unrecorded reference length"}.`} Green: stable prefix. Amber: variable. Red: stable content after the break.`}>
      {values.map((_, i) => <rect key={i} data-token={i} x={(i % columns) * 20} y={Math.floor(i / columns) * rowHeight}
        width="18" height="8" fill={tokenColor(initial.values[i] ?? values[i], i, values.length, initial.boundary)} />)}
      {boundary !== null && <g data-cache-marker data-boundary={boundary}
        transform={`translate(0 ${(initial.boundary ?? boundary) * height})`}>
        <line x1="0" x2={width} y1="0" y2="0" stroke="var(--accent)" strokeWidth="2" vectorEffect="non-scaling-stroke" />
      </g>}
    </svg>{boundary !== null && <span className="cache-marker-label" data-cache-label style={{ top: `${(26 + (initial.boundary ?? boundary) * height) / (height + 52) * 100}%` }}>Cache stops here</span>}</div>
    <figcaption>{first === null ? "No divergence finding is recorded; reuse is not inferred." : <>Earliest observed divergence: <strong>token {number(first)}</strong>.</>} {total ? <>Reference prompt: {number(total)} tokens.</> : "Reference length unrecorded."}</figcaption>
  </figure>;
}
