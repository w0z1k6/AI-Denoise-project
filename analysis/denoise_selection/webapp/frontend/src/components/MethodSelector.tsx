import { METHOD_GROUP_ORDER, METHOD_OPTIONS, methodHintKey } from "../lib/methodOptions";
import { useI18n } from "../i18n/I18nContext";
import type { DictKey } from "../i18n";

type Props = {
  value: string;
  onChange: (value: string) => void;
};

export default function MethodSelector({ value, onChange }: Props) {
  const { t } = useI18n();
  const hintKey = methodHintKey(value) as DictKey | "";
  const hint = hintKey ? t(hintKey) : "";
  const showEnv = value === "deepfilter";

  return (
    <div className="method-selector">
      <label className="field-label" htmlFor="method-select">
        {t("method")}
      </label>
      <div className="method-select-wrap">
        <select id="method-select" value={value} onChange={(e) => onChange(e.target.value)}>
          {METHOD_GROUP_ORDER.map((group) => (
            <optgroup key={group} label={t(`methodGroup_${group}` as DictKey)}>
              {METHOD_OPTIONS.filter((m) => m.group === group).map((m) => (
                <option key={m.value} value={m.value}>
                  {t(m.labelKey as DictKey)}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </div>
      {hint ? (
        <div className="method-lcd">
          {showEnv ? <span className="method-env-badge">ENV</span> : null}
          <span>{hint}</span>
        </div>
      ) : null}
    </div>
  );
}
