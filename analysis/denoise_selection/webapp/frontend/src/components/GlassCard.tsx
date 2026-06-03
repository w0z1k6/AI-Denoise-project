import type { PropsWithChildren, ReactNode } from "react";

type Props = PropsWithChildren<{
  className?: string;
  title?: ReactNode;
  subtitle?: ReactNode;
}>;

export default function GlassCard({ className = "", title, subtitle, children }: Props) {
  return (
    <section className={`glass-card ${className}`.trim()}>
      {(title || subtitle) && (
        <header className="glass-card-header">
          {title ? <h3 className="section-title">{title}</h3> : null}
          {subtitle ? <p className="section-subtitle">{subtitle}</p> : null}
        </header>
      )}
      {children}
    </section>
  );
}

