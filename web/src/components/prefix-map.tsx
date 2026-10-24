"use client";

import { useLayoutEffect, useMemo, useRef, useState } from "react";
import { gsap } from "gsap";
import { groupStability, tokenColor, tokenColors } from "@/lib/heatmap";
import { number } from "@/lib/workspace";
import { scannerParts, tapeParts, partDepth, scannerTransform, rulerTicks, groove, scanLine, type Part } from "./cache-scanner/geometry";
import type { SolidPaths } from "./iso/iso-kit";
import styles from "./cache-scanner/scanner.module.css";

type Props = { values: number[]; boundary: number | null; first: number | null; total?: number };
function Solid({ paths, color = "#e4e5dd", token }: { paths: SolidPaths; color?: string; token?: number }) {
  return <><path d={paths.fill} fill={token === undefined ? color : "#b9bdb2"} className={styles.solid} />
    {paths.shades.map((d, i) => <path key={i} d={d} fill="#30382b" opacity={0.06 + i * 0.06} />)}
    <path d={paths.top} fill={color} data-token={token} />
    <path d={paths.outline} className={styles.edge} /><path d={paths.crease} className={styles.edge} />
  </>;
}

export function PrefixMap({ values, boundary, first, total }: Props) {
  const root = useRef<HTMLElement>(null);
  const groups = useMemo(() => groupStability(values, tapeParts.length), [values]);
  const [initial] = useState(() => ({ fraction: boundary ?? 0, groups, count: values.length }));
  const positionRef = useRef({ value: initial.fraction });
  const fraction = boundary ?? 0;
  const parts = useMemo(() => [...scannerParts, ...tapeParts].sort((a, b) => partDepth(a, initial.fraction) - partDepth(b, initial.fraction)), [initial.fraction]);
  useLayoutEffect(() => {
    const figure = root.current;
    if (!figure) return;
    const preference = matchMedia("(prefers-reduced-motion: reduce)");
    const position = positionRef.current;
    let tween: gsap.core.Tween | undefined;
    let colorTween: gsap.core.Tween | undefined;
    let visible = false;
    const nodes = new Map([...figure.querySelectorAll<SVGGElement>("[data-part]")].map(node => [node.dataset.part!, node]));
    const layer = figure.querySelector("[data-assembly]");
    const readout = figure.querySelector("[data-scanner-readout]");
    const draw = () => {
      const transform = scannerTransform(position.value);
      figure.querySelectorAll("[data-moving]").forEach(node => node.setAttribute("transform", transform));
      // Sort complete solids at the current position so the bridge can cross the tape.
      const sorted = [...parts].sort((a, b) => partDepth(a, position.value) - partDepth(b, position.value));
      for (const part of sorted) { const node = nodes.get(part.id); if (node) layer?.appendChild(node); }
      figure.dataset.scannerPosition = String(position.value);
    };
    const settle = () => {
      position.value = fraction; draw();
      if (readout) readout.textContent = first === null ? "No recorded break" : `Stops at token ${number(first)}`;
    };
    const apply = () => {
      tween?.kill(); colorTween?.kill();
      const duration = preference.matches || !visible ? 0 : 0.9;
      colorTween = gsap.to(figure.querySelectorAll("[data-token]"), { fill: (_i: number, node: Element) => {
        const index = Number(node.getAttribute("data-token"));
        return groups[index] ? tokenColor(groups[index].stability, groups[index].end - 1, values.length, boundary) : "#ddd";
      }, duration, ease: "power3.out", overwrite: true });
      if (!duration) { settle(); return; }
      if (readout) readout.textContent = "Scanner moving…";
      tween = gsap.to(position, { value: fraction, duration, ease: "power3.out", onUpdate: draw, onComplete: settle });
    };
    const observer = new IntersectionObserver(entries => {
      visible = entries[entries.length - 1].isIntersecting;
      if (!visible) { tween?.kill(); colorTween?.progress(1); settle(); }
    }, { rootMargin: "120px" });
    observer.observe(figure);
    const box = figure.getBoundingClientRect(); visible = box.bottom > 0 && box.top < innerHeight;
    apply(); preference.addEventListener("change", apply);
    return () => { observer.disconnect(); preference.removeEventListener("change", apply); tween?.kill(); colorTween?.kill(); };
  }, [boundary, fraction, first, groups, values.length, initial.fraction, parts]);

  if (!groups.length) return <p>No aligned token data is recorded for this route.</p>;
  return <figure className={styles.figure} ref={root} data-cache-scanner data-scanner-position={initial.fraction}>
    <div className={styles.header}><span className={styles.title}>Prompt cache scanner</span><span className={styles.status}>SIMULATED · saved prompt structure</span></div>
    <svg className={styles.stage} viewBox="120 55 560 255" role="img" data-group-count={groups.length}
      aria-label={`Optical scanner on a prompt tape. ${first === null ? "No divergence is recorded." : `The probe stops at token ${number(first)} of ${total ? number(total) : "the recorded reference"}.`} Deep green is reusable; yellow varies; red is recomputed after the break.`}>
      <g data-assembly>{parts.map((part: Part) => {
        const index = tapeParts.findIndex(t => t.id === part.id);
        const g = groups[index], initialGroup = initial.groups[index];
        const state = g ? tokenColor(g.stability, g.end - 1, values.length, boundary) : undefined;
        const color = index >= 0 && initialGroup ? tokenColor(initialGroup.stability, initialGroup.end - 1, initial.count, initial.fraction) : part.color;
        return <g key={part.id} data-part={part.id} data-moving={part.moving ? "true" : undefined} transform={part.moving ? scannerTransform(initial.fraction) : undefined}>
          <Solid paths={part.paths} color={color} token={index >= 0 ? index : undefined} />
          {state === tokenColors.variable && <path d={tapeParts[index].slash} stroke="#4b3b00" strokeWidth="1.5" vectorEffect="non-scaling-stroke" />}
          {state === tokenColors.recomputed && <circle cx={tapeParts[index].mark[0]} cy={tapeParts[index].mark[1]} r="1.7" fill="#fff" />}
          {part.id === "ruler" && <path d={rulerTicks} className={styles.edge} />}
          {part.id === "bedplate" && <path d={groove} className={styles.edge} />}
          {part.id === "lens" && boundary !== null && <path d={scanLine} stroke="#2200ff" strokeWidth="2" vectorEffect="non-scaling-stroke" data-cache-marker data-boundary={boundary} />}
          {index >= 0 && <title>{total && g ? `Reference tokens approximately ${Math.floor(g.start / values.length * total)}–${Math.ceil(g.end / values.length * total)}. ` : ""}{g && tokenColor(g.stability, g.end - 1, values.length, boundary) === tokenColors.variable ? "Contains variation." : g && tokenColor(g.stability, g.end - 1, values.length, boundary) === tokenColors.reusable ? "Reusable prefix." : "Static content after the break."}</title>}
        </g>;
      })}</g>
    </svg>
    <div className={styles.footer}><span>BEFORE / AFTER moves the probe</span><span className={styles.readout} data-scanner-readout aria-hidden="true">{first === null ? "No recorded break" : `Stops at token ${number(first)}`}</span></div>
    <figcaption className={styles.caption}>{first === null ? "No cache break is inferred." : <>Cache stops here: <strong>token {number(first)}</strong>{total ? <> of {number(total)}</> : ""}.</>} The tape conservatively summarizes saved bins; the probe follows the exact recorded divergence. This is a schematic, not measured hardware.</figcaption>
  </figure>;
}
