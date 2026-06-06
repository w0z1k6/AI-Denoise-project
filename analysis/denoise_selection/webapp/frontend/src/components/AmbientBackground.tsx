import type { CSSProperties } from "react";
import { useRef } from "react";
import { useBackgroundMotion } from "../hooks/useBackgroundMotion";
import { useStudioPointer } from "../hooks/useStudioPointer";
import ClickRipples from "./ClickRipples";
import ScopeCanvas from "./ScopeCanvas";

const PARTICLES_FULL = Array.from({ length: 18 }, (_, i) => ({
  id: i,
  left: `${8 + ((i * 17) % 84)}%`,
  top: `${12 + ((i * 23) % 70)}%`,
  delay: `${(i * 0.35) % 4}s`,
  depth: 0.4 + (i % 5) * 0.15,
}));

const PARTICLES_LITE = PARTICLES_FULL.slice(0, 6);

type Props = {
  taskId?: string;
};

export default function AmbientBackground({ taskId = "" }: Props) {
  const atmosphereRef = useRef<HTMLDivElement>(null);
  const { mobile } = useBackgroundMotion(taskId);
  useStudioPointer(atmosphereRef);

  const particles = mobile ? PARTICLES_LITE : PARTICLES_FULL;

  return (
    <div ref={atmosphereRef} className="studio-atmosphere" aria-hidden="true">
      <div className="studio-cursor-glow" />
      <div className="studio-grid" />
      {!mobile ? <div className="studio-grid studio-grid-fine" /> : null}
      <div className="studio-scanline" />
      <div className="studio-grain" />
      <div className="studio-particles">
        {particles.map((p) => (
          <span
            key={p.id}
            className="studio-particle"
            style={
              {
                left: p.left,
                top: p.top,
                animationDelay: p.delay,
                "--depth": p.depth,
              } as CSSProperties
            }
          />
        ))}
      </div>
      {!mobile ? <ScopeCanvas /> : null}
      <ClickRipples />
    </div>
  );
}
