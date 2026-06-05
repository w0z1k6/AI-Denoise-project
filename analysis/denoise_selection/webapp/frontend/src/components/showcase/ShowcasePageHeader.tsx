import type { ReactNode } from "react";
import ShowcaseHero from "./ShowcaseHero";

type HubProps = {
  variant: "hub";
  eyebrow: string;
  title: string;
  lede?: string;
  actions?: ReactNode;
};

type InnerProps = {
  variant: "inner";
  moduleId: string;
  channel: string;
  title: string;
  subtitle?: string;
  badge?: ReactNode;
};

type Props = HubProps | InnerProps;

export default function ShowcasePageHeader(props: Props) {
  if (props.variant === "hub") {
    return (
      <ShowcaseHero
        eyebrow={props.eyebrow}
        title={props.title}
        lede={props.lede}
        actions={props.actions}
      />
    );
  }

  return (
    <header className="showcase-inner-header">
      <div className="showcase-inner-meta">
        <span className="rack-panel-id">
          {props.moduleId} / {props.channel}
        </span>
        {props.badge}
      </div>
      <h1 className="showcase-inner-title">{props.title}</h1>
      {props.subtitle ? <p className="showcase-inner-subtitle">{props.subtitle}</p> : null}
    </header>
  );
}
