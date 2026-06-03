import { createContext, useCallback, useContext, useEffect, useMemo, useState, type PropsWithChildren } from "react";
import { dict, type DictKey, type Lang } from "./index";

type Theme = "light" | "dark";

type I18nContextValue = {
  lang: Lang;
  theme: Theme;
  t: (key: DictKey) => string;
  setLang: (lang: Lang) => void;
  toggleLang: () => void;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
};

const I18nContext = createContext<I18nContextValue | null>(null);

function readLang(): Lang {
  const v = localStorage.getItem("ui_lang");
  return v === "en" ? "en" : "zh";
}

function readTheme(): Theme {
  const v = localStorage.getItem("ui_theme");
  if (v === "dark" || v === "light") return v;
  return "light";
}

export function I18nProvider({ children }: PropsWithChildren) {
  const [lang, setLangState] = useState<Lang>(readLang);
  const [theme, setThemeState] = useState<Theme>(readTheme);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    localStorage.setItem("ui_lang", l);
    document.documentElement.lang = l === "zh" ? "zh-CN" : "en";
  }, []);

  const setTheme = useCallback((t: Theme) => {
    setThemeState(t);
    localStorage.setItem("ui_theme", t);
    document.documentElement.setAttribute("data-theme", t);
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    document.documentElement.setAttribute("data-theme", theme);
  }, [lang, theme]);

  const toggleLang = useCallback(() => setLang(lang === "zh" ? "en" : "zh"), [lang, setLang]);
  const toggleTheme = useCallback(() => setTheme(theme === "light" ? "dark" : "light"), [theme, setTheme]);

  const t = useCallback((key: DictKey) => dict[lang][key], [lang]);

  const value = useMemo(
    () => ({ lang, theme, t, setLang, toggleLang, setTheme, toggleTheme }),
    [lang, theme, t, setLang, toggleLang, setTheme, toggleTheme],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
