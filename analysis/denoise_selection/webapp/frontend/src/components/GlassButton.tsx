import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

type Props = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: "primary" | "secondary" | "ghost" | "accent" | "danger";
  }
>;

export default function GlassButton({ variant = "secondary", className = "", children, ...rest }: Props) {
  return (
    <button className={`glass-btn glass-btn-${variant} ${className}`.trim()} {...rest}>
      {children}
    </button>
  );
}
