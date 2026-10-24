"use client";

import { useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { gsap } from "gsap";
import { groupStability, tileBoundary, tokenColor, tokenColors } from "@/lib/heatmap";
import { number } from "@/lib/workspace";

type Props = { values: number[]; boundary: number | null; first: number | null; total?: number };
const compactQuery = "(max-width: 600px)";
const subscribe = (callback: () => void) => {
  const query = window.matchMedia(compactQuery);
  query.addEventListener("change", callback);
  return () => query.removeEventListener("change", callback);
};

export function PrefixMap(props: Props) {
  const compact = useSyncExternalStore(subscribe, () => window.matchMedia(compactQuery).matches, () => false);
  const columns = compact ? 8 : 16;
  return <PrefixTiles key={columns} {...props} columns={columns} />;
}

function PrefixTiles({ values, boundary, first, total, columns: requestedColumns }: Props & { columns: number }) {
  const root = useRef<HTMLDivElement>(null);
  const groups = useMemo(() => groupStability(values, requestedColumns * 4), [values, requestedColumns]);
  const columns = Math.min(requestedColumns, groups.length || 1);
  const width = 1000, size = width / columns;
  const height = Math.ceil(groups.length / columns) * size;
  const color = (group: typeof groups[number], edge: number | null) => tokenColor(group.stability, group.end - 1, values.length, edge);
  const [initial] = useState(() => ({ groups, boundary }));
  const initialPosition = tileBoundary(initial.boundary ?? 0, groups.length, columns, size);
  useLayoutEffect(() => {
    const canvas = root.current;
    if (!canvas) return;
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    let tweens: gsap.core.Tween[] = [];
    const apply = () => {
      tweens.forEach(t => t.kill());
      const options = { duration: preference.matches ? 0 : 0.6, ease: "power3.out", overwrite: true };
      tweens = [gsap.to(canvas.querySelectorAll("[data-token]"), {
        ...options, fill: (i: number) => tokenColor(groups[i].stability, groups[i].end - 1, values.length, boundary),
      })];
      if (boundary !== null) {
        const position = tileBoundary(boundary, groups.length, columns, size);
        tweens.push(gsap.to(canvas.querySelector("[data-cache-marker]"), { ...options, attr: { transform: `translate(0 ${position.y})` } }));
        tweens.push(gsap.to(canvas.querySelectorAll("[data-cache-path]"), { ...options, attr: { d: `M0 0 H${position.x} M${position.x} 0 V${size}` } }));
        tweens.push(gsap.to(canvas.querySelector("[data-cache-label]"), { ...options, top: `${(26 + position.y) / (height + 52) * 100}%` }));
      }
    };
    apply(); preference.addEventListener("change", apply);
    return () => { preference.removeEventListener("change", apply); tweens.forEach(t => t.kill()); };
  }, [groups, values.length, boundary, columns, size, height]);

  if (!groups.length) return <p>No aligned token data is recorded for this route.</p>;
  return <figure className="prefix-map">
    <div className="prefix-canvas" ref={root}><svg viewBox={`0 -26 ${width} ${height + 52}`} role="img" data-group-count={groups.length}
      aria-label={`SIMULATED grouped prefix map, read across then down. ${groups.length} squares summarize contiguous saved bins. ${first === null ? "No divergence recorded." : `Cache break at reference token ${first} of ${total ?? "unrecorded length"}.`} Plain deep green: fully stable prefix; yellow with a slash: contains variation; red with a dot: stable content after the break.`}>
      {groups.map((group, i) => {
        const x = (i % columns) * size, y = Math.floor(i / columns) * size;
        const state = color(group, boundary);
        return <g key={i}><rect data-token={i} x={x} y={y} width={size - 5} height={size - 5}
          stroke="#374151" strokeWidth="0.75" vectorEffect="non-scaling-stroke" fill={color(initial.groups[i] ?? group, initial.boundary)}>
          <title>{total ? `Approximate reference tokens ${Math.floor(group.start / values.length * total)}–${Math.ceil(group.end / values.length * total)}.` : "Contiguous saved reference bins."} {group.stability < 1 ? "Contains variation." : "Static content."}</title>
        </rect>
        {state === tokenColors.variable && <path d={`M${x + size * 0.3} ${y + size * 0.7} L${x + size * 0.7} ${y + size * 0.3}`} stroke="#4b3b00" strokeWidth="1.5" vectorEffect="non-scaling-stroke" pointerEvents="none" />}
        {state === tokenColors.recomputed && <circle cx={x + (size - 5) / 2} cy={y + (size - 5) / 2} r={size * 0.055} fill="#fff" pointerEvents="none" />}
        </g>;
      })}
      {boundary !== null && <g data-cache-marker data-boundary={boundary} transform={`translate(0 ${initialPosition.y})`}>
        {["var(--background)", "var(--accent)"].map((stroke, i) => <path key={stroke} data-cache-path
          d={`M0 0 H${initialPosition.x} M${initialPosition.x} 0 V${size}`} fill="none" stroke={stroke} strokeWidth={i ? 2 : 5} vectorEffect="non-scaling-stroke" />)}
      </g>}
    </svg>{boundary !== null && <span className="cache-marker-label" data-cache-label style={{ top: `${(26 + initialPosition.y) / (height + 52) * 100}%` }}>Cache stops here</span>}</div>
    <figcaption>{first === null ? "No divergence is recorded; reuse is not inferred." : <>Cache break: <strong>token {number(first)}</strong>{total ? <> of {number(total)}</> : ""}.</>} Each square groups neighboring reference bins.</figcaption>
  </figure>;
}
