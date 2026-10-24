"use client";

import { useLayoutEffect, useRef } from "react";
import { gsap } from "gsap";

import { formatMetric, type MetricUnit } from "@/lib/heatmap";

export function MeasuredNumber({ value, unit }: { value: number; unit: MetricUnit }) {
  const ref = useRef<HTMLSpanElement>(null);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const final = formatMetric(value, unit);
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    let tween: gsap.core.Tween | undefined;
    let observer: IntersectionObserver | undefined;
    const settle = () => { tween?.kill(); el.textContent = final; };
    // A new view must show its saved value even before it enters the viewport.
    // Cleanup only cancels motion; writing an old value there can overwrite React's update.
    settle();
    const animate = () => {
      if (preference.matches) { settle(); return; }
      const counter = { value: 0 };
      tween = gsap.to(counter, { value, duration: 0.55, ease: "power3.out", onUpdate: () => { el.textContent = formatMetric(counter.value, unit); }, onComplete: () => { el.textContent = final; } });
    };
    if (preference.matches) settle();
    else {
      observer = new IntersectionObserver(entries => { if (entries.some(e => e.isIntersecting)) { observer?.disconnect(); animate(); } }, { threshold: 0.2 });
      observer.observe(el);
    }
    preference.addEventListener("change", settle);
    return () => { observer?.disconnect(); preference.removeEventListener("change", settle); tween?.kill(); };
  }, [value, unit]);
  // Accessible text always gives the saved result. Visual interpolation is transient only.
  return <><span ref={ref} aria-hidden="true" data-measured-value={value}>{formatMetric(value, unit)}</span><span className="sr-only">{formatMetric(value, unit)}</span></>;
}
