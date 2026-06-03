type Props = {
  label: string;
  value: string;
  className?: string;
};

export default function StatChip({ label, value, className = "" }: Props) {
  return (
    <div className={`stat-chip ${className}`.trim()}>
      <span className="stat-chip-label">{label}</span>
      <strong className="stat-chip-value">{value}</strong>
    </div>
  );
}
