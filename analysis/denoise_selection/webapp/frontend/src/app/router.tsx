import type { ReactElement } from "react";
import { Route, Routes } from "react-router-dom";
import ChartCenterPage from "../pages/ChartCenterPage";
import HistoryPage from "../pages/HistoryPage";
import HomePage from "../pages/HomePage";
import ResultOverviewPage from "../pages/ResultOverviewPage";
import TaskProgressPage from "../pages/TaskProgressPage";
import UploadConfigPage from "../pages/UploadConfigPage";

type Props = {
  taskId: string;
  setTaskId: (taskId: string) => void;
};

export function AppRoutes({ taskId, setTaskId }: Props): ReactElement {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/upload" element={<UploadConfigPage setTaskId={setTaskId} />} />
      <Route path="/progress" element={<TaskProgressPage taskId={taskId} />} />
      <Route path="/overview" element={<ResultOverviewPage taskId={taskId} />} />
      <Route path="/charts" element={<ChartCenterPage taskId={taskId} />} />
      <Route path="/history" element={<HistoryPage setTaskId={setTaskId} />} />
    </Routes>
  );
}
