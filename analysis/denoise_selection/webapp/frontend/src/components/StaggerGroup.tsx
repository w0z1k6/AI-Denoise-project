import { Children, type CSSProperties, type ReactNode } from "react";

type Props = {
  children: ReactNode;
  className?: string;
  fast?: boolean;
};

export default function StaggerGroup({ children, className = "", fast = false }: Props) {
  const items = Children.toArray(children).filter(Boolean);

  return (
    <div className={`${fast ? "stagger-fast" : "stagger"} ${className}`.trim()}>
      {items.map((child, index) => (
        <div key={index} className="stagger-item" style={{ "--stagger-i": index } as CSSProperties}>
          {child}
        </div>
      ))}
    </div>
  );
}
