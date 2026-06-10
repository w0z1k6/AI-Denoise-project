import type { ReactElement } from "react";
import { Route, Routes } from "react-router-dom";
import ChartCenterPage from "../pages/ChartCenterPage";
import HistoryPage from "../pages/HistoryPage";
import HomePage from "../pages/HomePage";
import ResultOverviewPage from "../pages/ResultOverviewPage";
import AlgorithmAtlasPage from "../pages/showcase/AlgorithmAtlasPage";
import CompareCinemaPage from "../pages/showcase/CompareCinemaPage";
import PipelineTheaterPage from "../pages/showcase/PipelineTheaterPage";
import ShowcaseHubPage from "../pages/showcase/ShowcaseHubPage";
import SignalMonitorPage from "../pages/showcase/SignalMonitorPage";
import TaskProgressPage from "../pages/TaskProgressPage";
import LiveCapturePage from "../pages/LiveCapturePage";
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
      <Route path="/record" element={<LiveCapturePage setTaskId={setTaskId} />} />
      <Route path="/progress" element={<TaskProgressPage taskId={taskId} />} />
      <Route path="/overview" element={<ResultOverviewPage taskId={taskId} />} />
      <Route path="/charts" element={<ChartCenterPage taskId={taskId} />} />
      <Route path="/history" element={<HistoryPage setTaskId={setTaskId} />} />
      <Route path="/showcase" element={<ShowcaseHubPage taskId={taskId} />} />
      <Route path="/showcase/algorithms" element={<AlgorithmAtlasPage />} />
      <Route path="/showcase/pipeline" element={<PipelineTheaterPage taskId={taskId} />} />
      <Route path="/showcase/monitor" element={<SignalMonitorPage taskId={taskId} />} />
      <Route path="/showcase/cinema" element={<CompareCinemaPage taskId={taskId} />} />
    </Routes>
  );
}
