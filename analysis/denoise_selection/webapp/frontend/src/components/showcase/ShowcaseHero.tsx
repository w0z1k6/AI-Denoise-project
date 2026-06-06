import type { ReactNode } from "react";

type Props = {
  eyebrow: string;
  title: string;
  lede?: string;
  actions?: ReactNode;
};

export default function ShowcaseHero({ eyebrow, title, lede, actions }: Props) {
  return (
    <header className="showcase-hero">
      <p className="console-eyebrow">{eyebrow}</p>
      <h1 className="showcase-hero-title">{title}</h1>
      {lede ? <p className="showcase-hero-lede">{lede}</p> : null}
      {actions ? <div className="showcase-hero-actions">{actions}</div> : null}
    </header>
  );
}
