"use client";

import { useLayoutEffect, useRef, type ReactNode } from "react";
import { gsap } from "gsap";

export function SummaryReveal({ children, className }: { children: ReactNode; className: string }) {
  const root = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    const el = root.current;
    if (!el) return;
    const media = gsap.matchMedia();
    media.add("(prefers-reduced-motion: no-preference)", () => {
      gsap.fromTo(el.children, { opacity: 0.7, y: 6 }, { opacity: 1, y: 0, duration: 0.35, stagger: 0.05, ease: "power3.out", clearProps: "opacity,transform" });
    });
    return () => media.revert();
  }, []);
  return <div ref={root} className={className}>{children}</div>;
}
