import type { ReactNode } from "react";

/** Highlight keyword matches in chart titles (case-insensitive). */
export function highlightText(text: string, keyword: string): ReactNode {
  const kw = keyword.trim();
  if (!kw) return text;
  const lower = text.toLowerCase();
  const kwLower = kw.toLowerCase();
  const idx = lower.indexOf(kwLower);
  if (idx < 0) return text;
  return (
    <>
      {text.slice(0, idx)}
      <mark>{text.slice(idx, idx + kw.length)}</mark>
      {text.slice(idx + kw.length)}
    </>
  );
}
