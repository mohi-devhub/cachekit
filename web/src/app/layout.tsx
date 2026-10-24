import type { Metadata } from "next";
import Link from "next/link";
import { SiteNav } from "@/components/site-nav";
import "./fonts.css";
import "lenis/dist/lenis.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "cachekit — Prompt cache analysis",
  description: "Find what breaks prompt-cache reuse, verify a fix, and measure the difference.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <a href="#main" className="skip-link">Skip to content</a>
        <div className="app-shell"><div className="frame-guides" aria-hidden="true"><i /><i /><i /><i /></div><header className="site-header">
          <Link href="/" className="wordmark" aria-label="cachekit home">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
              <path d="M3 5h18M3 12h12M3 19h6" fill="none" stroke="currentColor" strokeWidth="3" />
            </svg>
            cachekit
          </Link>
          <SiteNav />
        </header>
        <div className="main-column"><main id="main" className="workspace">{children}</main>
        <footer className="site-footer">Analyze locally. Review the fix. Measure the result.</footer>
        </div></div>
      </body>
    </html>
  );
}
