import type { PropsWithChildren, ReactNode } from "react";

export type RackLed = "active" | "processing" | "error" | "idle";

type Props = PropsWithChildren<{
  moduleId: string;
  channel: string;
  led?: RackLed;
  title?: ReactNode;
  subtitle?: ReactNode;
  className?: string;
  alert?: boolean;
}>;

export default function RackPanel({
  moduleId,
  channel,
  led = "active",
  title,
  subtitle,
  className = "",
  alert = false,
  children,
}: Props) {
  return (
    <section className={`rack-panel glass-card rack-no-corner-led ${alert ? "rack-panel-alert" : ""} ${className}`.trim()}>
      <div className="rack-panel-head">
        <span className="rack-panel-id">
          {moduleId} / {channel}
        </span>
        <span className={`rack-led rack-led-${led}`} aria-hidden="true" />
      </div>
      {(title || subtitle) && (
        <header className="glass-card-header rack-panel-title-block">
          {title ? <h3 className="section-title">{title}</h3> : null}
          {subtitle ? <p className="section-subtitle">{subtitle}</p> : null}
        </header>
      )}
      {children}
    </section>
  );
}
