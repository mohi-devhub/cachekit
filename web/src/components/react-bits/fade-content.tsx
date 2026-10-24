"use client";

// Adapted from React Bits FadeContent's mount/fade path at e12c22192ac7b4b452c5e2feb9b586d74765d696.
// Copyright (c) 2026 David Haz. License: /licenses/React-Bits-LICENSE.md.
// Reduced to one brief hero fade; no filters, ScrollTrigger, noise or repeating effects.
import { useLayoutEffect, useRef, type ReactNode } from "react";
import { gsap } from "gsap";

export function FadeContent({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    const media = gsap.matchMedia();
    media.add("(prefers-reduced-motion: no-preference)", () => {
      gsap.fromTo(el, { opacity: 0.65 }, { opacity: 1, duration: 0.45, ease: "power3.out", clearProps: "opacity" });
    });
    return () => media.revert();
  }, []);
  return <div ref={ref}>{children}</div>;
}
