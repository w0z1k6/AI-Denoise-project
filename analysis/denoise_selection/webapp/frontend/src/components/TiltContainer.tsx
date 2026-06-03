import { useCallback, useRef, type MouseEvent, type PropsWithChildren } from "react";

type Props = PropsWithChildren<{
  className?: string;
  motionRange?: number;
}>;

export default function TiltContainer({ children, className = "", motionRange = 22 }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const onMove = useCallback(
    (e: MouseEvent<HTMLDivElement>) => {
      if (reduced || !ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const xOffset = (e.clientX - cx) / (rect.width / 2);
      const yOffset = (e.clientY - cy) / (rect.height / 2);
      const rotateX = -yOffset * motionRange;
      const rotateY = xOffset * motionRange;
      ref.current.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    },
    [motionRange, reduced],
  );

  const onLeave = useCallback(() => {
    if (!ref.current) return;
    ref.current.style.transform = "rotateX(0deg) rotateY(0deg)";
  }, []);

  return (
    <div className={`tilt-container ${className}`.trim()} ref={ref} onMouseMove={onMove} onMouseLeave={onLeave}>
      {children}
    </div>
  );
}
