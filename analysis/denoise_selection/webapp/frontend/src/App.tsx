import { useState } from "react";
import AppShell from "./AppShell";

export default function App() {
  const [taskId, setTaskId] = useState<string>(localStorage.getItem("task_id") ?? "");

  const updateTaskId = (v: string) => {
    setTaskId(v);
    localStorage.setItem("task_id", v);
  };

  return <AppShell taskId={taskId} setTaskId={updateTaskId} />;
}
