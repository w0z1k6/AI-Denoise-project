import { useMemo, useState } from "react";
import { useI18n } from "../i18n/I18nContext";
import GlassButton from "./GlassButton";
import GlassCard from "./GlassCard";

type Props = {
  onRecord: (xIs: "A" | "B", guess: "A" | "B") => Promise<void>;
  stats: { accuracy: number; total: number; correct: number };
};

export default function ABXTestPanel({ onRecord, stats }: Props) {
  const { t } = useI18n();
  const [seed, setSeed] = useState(0);
  const xIs = useMemo<"A" | "B">(() => (Math.random() > 0.5 ? "A" : "B"), [seed]);

  const submit = async (guess: "A" | "B") => {
    await onRecord(xIs, guess);
    setSeed((v) => v + 1);
  };

  return (
    <GlassCard title={t("abxTitle")} subtitle={t("abxSubtitle")}>
      <p className="muted">{t("abxHint")}</p>
      <p className="muted">
        {t("abxCurrent")}: <strong>{xIs}</strong> {t("abxDebug")}
      </p>
      <div className="row gap">
        <GlassButton variant="primary" onClick={() => submit("A")}>
          {t("guessA")}
        </GlassButton>
        <GlassButton variant="secondary" onClick={() => submit("B")}>
          {t("guessB")}
        </GlassButton>
      </div>
      <p className="muted">
        {t("accuracy")}: {(stats.accuracy * 100).toFixed(1)}% ({stats.correct}/{stats.total})
      </p>
    </GlassCard>
  );
}
