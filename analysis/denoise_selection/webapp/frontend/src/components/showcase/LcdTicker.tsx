type Props = {
  lines: string[];
};

export default function LcdTicker({ lines }: Props) {
  const text = lines.filter(Boolean).join("  ·  ");
  if (!text) return null;
  return (
    <div className="lcd-ticker" aria-live="polite">
      <div className="lcd-ticker-inner">
        <span>{text}</span>
        <span aria-hidden="true">{text}</span>
      </div>
    </div>
  );
}
