import { useState } from "react";
import { useI18n } from "../i18n/I18nContext";
import GlassButton from "./GlassButton";
import GlassCard from "./GlassCard";

type Props = {
  bookmarks: { time_sec: number; note: string }[];
  onAdd: (timeSec: number, note: string) => Promise<void>;
};

export default function BookmarkList({ bookmarks, onAdd }: Props) {
  const { t } = useI18n();
  const [timeSec, setTimeSec] = useState(0);
  const [note, setNote] = useState("");

  return (
    <GlassCard title={t("bookmarkTitle")} subtitle={t("bookmarkSubtitle")}>
      <div className="row gap">
        <input type="number" value={timeSec} step={0.01} onChange={(e) => setTimeSec(Number(e.target.value))} />
        <input value={note} placeholder={t("bookmarkPlaceholder")} onChange={(e) => setNote(e.target.value)} />
        <GlassButton
          variant="secondary"
          onClick={async () => {
            await onAdd(timeSec, note);
            setNote("");
          }}
        >
          {t("add")}
        </GlassButton>
      </div>
      <ul>
        {bookmarks.map((b, i) => (
          <li key={`${b.time_sec}_${i}`}>
            {b.time_sec.toFixed(2)}s - {b.note}
          </li>
        ))}
      </ul>
    </GlassCard>
  );
}
