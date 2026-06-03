import { render, screen } from "@testing-library/react";
import ABXTestPanel from "../components/ABXTestPanel";
import { I18nProvider } from "../i18n/I18nContext";

describe("ABXTestPanel", () => {
  it("renders stats and action buttons", () => {
    render(
      <I18nProvider>
        <ABXTestPanel onRecord={async () => undefined} stats={{ accuracy: 0.5, total: 10, correct: 5 }} />
      </I18nProvider>,
    );
    expect(screen.getByText("ABX 盲听测试")).toBeTruthy();
    expect(screen.getByText(/准确率: 50\.0%/)).toBeTruthy();
    expect(screen.getByText("猜 A")).toBeTruthy();
    expect(screen.getByText("猜 B")).toBeTruthy();
  });
});
