import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { I18nProvider } from "./i18n/I18nContext";
import "./styles.css";

const savedTheme = localStorage.getItem("ui_theme");
document.documentElement.setAttribute("data-theme", savedTheme === "dark" ? "dark" : "light");
document.documentElement.lang = localStorage.getItem("ui_lang") === "en" ? "en" : "zh-CN";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <I18nProvider>
        <App />
      </I18nProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
