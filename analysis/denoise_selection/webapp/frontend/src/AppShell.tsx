import { Link, useLocation } from "react-router-dom";
import { AppRoutes } from "./app/router";
import AmbientBackground from "./components/AmbientBackground";
import GlassNav from "./components/GlassNav";

type Props = {
  taskId: string;
  setTaskId: (v: string) => void;
};

function PageTransition({ taskId, setTaskId }: Props) {
  const location = useLocation();
  return (
    <div className="page-route" key={location.pathname}>
      <AppRoutes taskId={taskId} setTaskId={setTaskId} />
    </div>
  );
}

type AppProps = {
  taskId: string;
  setTaskId: (v: string) => void;
};

export default function AppShell({ taskId, setTaskId }: AppProps) {
  return (
    <div className="app">
      <AmbientBackground taskId={taskId} />
      <GlassNav currentTaskId={taskId} />
      <main className="page-shell">
        <PageTransition taskId={taskId} setTaskId={setTaskId} />
      </main>
    </div>
  );
}
