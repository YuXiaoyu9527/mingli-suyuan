"use client";

import Link from "next/link";

export default function ReportPage() {
  return (
    <div className="p-6 min-h-dvh space-y-5 max-w-sm mx-auto text-center pt-20">
      <h1 className="text-2xl font-[var(--font-display)] text-[var(--color-accent)]">Your Full Report</h1>
      <p className="text-text-secondary text-sm">
        Go back to the home page and reveal your element first.
        Your complete personality blueprint will appear here.
      </p>
      <Link href="/" className="btn-primary inline-flex">
        ← Back to Home
      </Link>
    </div>
  );
}
