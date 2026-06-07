import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import GlassButton from "../../components/GlassButton";
import RackPanel from "../../components/RackPanel";
import SceneCard from "../../components/showcase/SceneCard";
import ShowcasePageHeader from "../../components/showcase/ShowcasePageHeader";
import ShowcaseSubNav from "../../components/showcase/ShowcaseSubNav";
import { useI18n } from "../../i18n/I18nContext";
import { SCENE_PRESETS, applySceneToUpload, type ScenePreset } from "../../lib/scenePresets";

type Props = {
  taskId: string;
};

export default function SceneVaultPage({ taskId }: Props) {
  const { t } = useI18n();
  const nav = useNavigate();
  const [selected, setSelected] = useState<ScenePreset>(SCENE_PRESETS[0]);
  const [tagFilter, setTagFilter] = useState<string>("all");

  const tagKeys = Array.from(new Set(SCENE_PRESETS.map((s) => s.tagKey)));
  const filtered =
    tagFilter === "all" ? SCENE_PRESETS : SCENE_PRESETS.filter((s) => s.tagKey === tagFilter);

  const loadUpload = () => {
    applySceneToUpload(selected);
    nav("/upload");
  };

  return (
    <div className="showcase-page showcase-page-inner stagger-fast">
      <ShowcaseSubNav />
      <ShowcasePageHeader
        variant="inner"
        moduleId="MOD-S05"
        channel="SCENES"
        title={t("sceneVaultTitle")}
        subtitle={t("sceneVaultSubtitle")}
        badge={<span className="showcase-sim-badge">{t("showcaseSimBadge")}</span>}
      />
      <RackPanel moduleId="MOD-S05" channel="SCENE VAULT" led="active">
        <div className="scene-vault-filters">
          <button
            type="button"
            className={`scene-filter-pill ${tagFilter === "all" ? "is-active" : ""}`}
            onClick={() => setTagFilter("all")}
          >
            {t("sceneFilterAll")}
          </button>
          {tagKeys.map((tag) => (
            <button
              key={tag}
              type="button"
              className={`scene-filter-pill ${tagFilter === tag ? "is-active" : ""}`}
              onClick={() => setTagFilter(tag)}
            >
              {t(tag)}
            </button>
          ))}
        </div>
        <div className="scene-vault-grid">
          {filtered.map((preset) => (
            <SceneCard
              key={preset.id}
              preset={preset}
              selected={selected.id === preset.id}
              onSelect={() => setSelected(preset)}
            />
          ))}
        </div>
        <div className="scene-vault-actions">
          <GlassButton variant="primary" onClick={loadUpload}>
            {t("sceneLoadUpload")}
          </GlassButton>
          {taskId ? (
            <Link to="/showcase/cinema" className="glass-btn glass-btn-secondary">
              {t("sceneOpenCinema")}
            </Link>
          ) : (
            <Link to="/upload" className="glass-btn glass-btn-ghost">
              {t("goUpload")}
            </Link>
          )}
        </div>
        <p className="muted scene-vault-hint">{t("sceneVaultHint")}</p>
      </RackPanel>
    </div>
  );
}
