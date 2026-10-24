"use client";

import { useEffect } from "react";

export function OverviewMotion() {
  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: no-preference) and (pointer: fine)");
    let disposed = false;
    let instance: import("lenis").default | undefined;
    let generation = 0;
    const update = async () => {
      const current = ++generation;
      instance?.destroy(); instance = undefined;
      if (!preference.matches || document.hidden) return;
      // Native scrolling is the fallback if the optional local chunk is unavailable.
      const { default: Lenis } = await import("lenis").catch(() => ({ default: null }));
      if (!Lenis) return;
      if (disposed || current !== generation) return;
      instance = new Lenis({
        autoRaf: true, lerp: 0.12, syncTouch: false, anchors: true,
        prevent: node => Boolean(node.closest("pre, textarea, .table-scroll, [data-lenis-prevent]")),
      });
    };
    void update();
    preference.addEventListener("change", update);
    document.addEventListener("visibilitychange", update);
    return () => { disposed = true; generation++; instance?.destroy(); preference.removeEventListener("change", update); document.removeEventListener("visibilitychange", update); };
  }, []);
  return null;
}
