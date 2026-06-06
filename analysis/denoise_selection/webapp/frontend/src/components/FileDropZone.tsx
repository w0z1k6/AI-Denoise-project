import { useRef, useState } from "react";
import { useI18n } from "../i18n/I18nContext";
import type { AudioFileMeta } from "../lib/audioMeta";

type Props = {
  file: File | null;
  meta: AudioFileMeta | null;
  onFile: (file: File | null) => void;
};

export default function FileDropZone({ file, meta, onFile }: Props) {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const pick = (f: File | null) => {
    if (!f) return;
    const ok = /\.(wav|mp3|flac)$/i.test(f.name);
    if (!ok) return;
    onFile(f);
  };

  return (
    <div
      className={`file-drop ${dragOver ? "file-drop-active" : ""} ${file ? "file-drop-filled" : ""}`}
      role="button"
      tabIndex={0}
      onClick={() => inputRef.current?.click()}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
      }}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        pick(e.dataTransfer.files?.[0] ?? null);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".wav,.mp3,.flac,audio/*"
        className="file-drop-input"
        onChange={(e) => pick(e.target.files?.[0] ?? null)}
      />
      <div className="file-drop-icon" aria-hidden="true" />
      <div className="file-drop-wave-deco" aria-hidden="true" />
      {file ? (
        <div className="file-drop-body">
          <strong>{file.name}</strong>
          <span className="muted">
            {meta?.sizeKb ?? Math.round(file.size / 1024)} KB
            {meta?.durationSec != null ? ` · ${meta.durationSec}s` : ""}
            {meta?.sampleRate != null ? ` · ${meta.sampleRate} Hz` : ""}
          </span>
        </div>
      ) : (
        <div className="file-drop-body">
          <strong>{t("dropTitle")}</strong>
          <span className="muted">{t("dropHint")}</span>
        </div>
      )}
      {file ? (
        <button
          type="button"
          className="file-drop-clear"
          onClick={(e) => {
            e.stopPropagation();
            onFile(null);
          }}
        >
          {t("dropClear")}
        </button>
      ) : null}
    </div>
  );
}
