"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef, useState } from "react";

export function SiteNav() {
  const path = usePathname();
  const [menu, setMenu] = useState({ path: "", open: false });
  const toggle = useRef<HTMLButtonElement>(null);
  const open = menu.path === path && menu.open;
  const close = () => setMenu({ path, open: false });
  const links: [string, string, boolean][] = [
    ["/", "Overview", path === "/"],
    ["/report/demo-before", "Findings", path.startsWith("/report/") && !path.includes("/heatmap/")],
    ["/report/demo-before/heatmap/helpdesk.answer", "Heatmap", path.includes("/heatmap/")],
    ["/bench", "Benchmarks", path === "/bench"],
    ["/fix", "Verify", path.startsWith("/fix")],
    ["/how-it-works", "Method", path === "/how-it-works"],
  ];
  return <><button ref={toggle} className="menu-toggle" aria-expanded={open} aria-controls="site-navigation"
    onClick={() => setMenu({ path, open: !open })}>{open ? "Close" : "Menu"}</button>
    <nav id="site-navigation" data-open={open} aria-label="Main navigation" onKeyDown={e => { if (e.key === "Escape") { close(); toggle.current?.focus(); } }}>
      {links.map(([href, text, active]) => <Link key={href} href={href} onClick={close} aria-current={active ? "page" : undefined}>{text}</Link>)}
      <a className="sidebar-action" href="https://github.com/mohi-devhub/cachekit" target="_blank" rel="noopener noreferrer" onClick={close}>Open repo</a>
    </nav></>;
}
