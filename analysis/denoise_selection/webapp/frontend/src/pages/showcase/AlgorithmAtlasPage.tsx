import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import GlassButton from "../../components/GlassButton";
import RackPanel from "../../components/RackPanel";
import MiniScope from "../../components/showcase/MiniScope";
import RackModuleGrid from "../../components/showcase/RackModuleGrid";
import ShowcasePageHeader from "../../components/showcase/ShowcasePageHeader";
import ShowcaseSubNav from "../../components/showcase/ShowcaseSubNav";
import { useI18n } from "../../i18n/I18nContext";
import type { DictKey } from "../../i18n";
import { METHOD_GROUP_ORDER, METHOD_OPTIONS } from "../../lib/methodOptions";

const GROUP_CODES: Record<string, string> = {
  recommended: "GRP-REC",
  math: "GRP-MATH",
  dl: "GRP-DL",
  baseline: "GRP-BASE",
};

const METHOD_PREFILL_KEY = "upload_method_prefill";

export default function AlgorithmAtlasPage() {
  const { t } = useI18n();
  const nav = useNavigate();
  const [selected, setSelected] = useState("auto");

  const selectedOpt = METHOD_OPTIONS.find((m) => m.value === selected);
  const hint = selectedOpt ? t(selectedOpt.hintKey as DictKey) : "";
  const label = selectedOpt ? t(selectedOpt.labelKey as DictKey) : "";

  const groups = useMemo(
    () =>
      METHOD_GROUP_ORDER.map((group) => ({
        group,
        code: GROUP_CODES[group] ?? group,
        title: t(`methodGroup_${group}` as DictKey),
        modules: METHOD_OPTIONS.filter((m) => m.group === group).map((m) => ({
          id: m.value,
          value: m.value,
          label: t(m.labelKey as DictKey),
          hint: t(m.hintKey as DictKey),
          selected: m.value === selected,
          onSelect: () => setSelected(m.value),
        })),
      })),
    [selected, t],
  );

  const freqMul = selected === "deepfilter" ? 1.6 : selected.includes("omlsa") ? 1.2 : 1;

  const goUploadWithMethod = () => {
    sessionStorage.setItem(METHOD_PREFILL_KEY, selected);
    nav("/upload");
  };

  return (
    <div className="showcase-page showcase-page-inner stagger-fast">
      <ShowcaseSubNav />
      <ShowcasePageHeader
        variant="inner"
        moduleId="MOD-S01"
        channel="ATLAS"
        title={t("showcaseAlgoTitle")}
        subtitle={t("showcaseAlgoSubtitle")}
      />
      {selected === "deepfilter" ? (
        <div className="showcase-env-bar">
          <span className="method-env-badge">ENV</span>
          <span>DEEPFILTER_CONDA_ENV=dfnet311</span>
        </div>
      ) : null}
      <div className="atlas-layout">
        <RackPanel moduleId="MOD-S01" channel="ATLAS" led="active" className="rack-no-corner-led">
          {groups.map((g) => (
            <section key={g.group} className="atlas-group">
              <div className="atlas-group-head">
                <div>
                  <span className="atlas-group-code">{g.code}</span>
                  <h4 className="section-title atlas-group-title">{g.title}</h4>
                </div>
                {g.group === selectedOpt?.group ? <MiniScope height={32} freqMul={freqMul} /> : null}
              </div>
              <RackModuleGrid modules={g.modules} />
              {g.group === selectedOpt?.group ? (
                <aside className="atlas-drawer-mobile is-open">
                  <h4>{label}</h4>
                  <p>{hint || t("showcaseAlgoPick")}</p>
                </aside>
              ) : null}
            </section>
          ))}
          <div className="atlas-upload-cta">
            <GlassButton variant="primary" onClick={goUploadWithMethod}>
              {t("showcaseGoUploadWithMethod")}
            </GlassButton>
          </div>
        </RackPanel>
        <aside className="atlas-drawer atlas-drawer-desktop is-open">
          <h4>{label}</h4>
          <p>{hint || t("showcaseAlgoPick")}</p>
          <Link to="/upload" className="muted" onClick={() => sessionStorage.setItem(METHOD_PREFILL_KEY, selected)}>
            {t("showcaseGoUploadWithMethod")}
          </Link>
        </aside>
      </div>
    </div>
  );
}
