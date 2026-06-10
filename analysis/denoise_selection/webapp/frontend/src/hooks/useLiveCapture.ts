import { useCallback, useEffect, useRef, useState } from "react";
import type { CapturePhase } from "../components/live/RecordTransport";
import {
  commitRecordSession,
  createRecordSession,
  finishRecordSession,
  recordAudioUrl,
  recordStreamUrl,
} from "../lib/api";
import {
  CHUNK_SAMPLES,
  MAX_RECORD_SEC,
  TARGET_SAMPLE_RATE,
  downsampleTo16k,
  float32ToPcmB64,
  pcmB64ToFloat32,
  rmsLevel,
} from "../lib/pcmUtils";
import type { ProcessRequest } from "../types/api";

const MAX_PENDING_CHUNKS = 8;

type PreviewUrls = { raw: string; preview: string } | null;

export function useLiveCapture() {
  const [phase, setPhase] = useState<CapturePhase>("idle");
  const [sessionId, setSessionId] = useState("");
  const [timerSec, setTimerSec] = useState(0);
  const [inputLevel, setInputLevel] = useState(0);
  const [outputLevel, setOutputLevel] = useState(0);
  const [levelDb, setLevelDb] = useState(-60);
  const [latencyMs, setLatencyMs] = useState(0);
  const [ancEnabled, setAncEnabled] = useState(false);
  const [ancDegraded, setAncDegraded] = useState(false);
  const [micError, setMicError] = useState("");
  const [previewUrls, setPreviewUrls] = useState<PreviewUrls>(null);
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);

  const streamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const seqRef = useRef(0);
  const pendingRef = useRef(0);
  const bufferRef = useRef<Float32Array>(new Float32Array(0));
  const monitorTimeRef = useRef(0);
  const timerRef = useRef<number | null>(null);
  const totalSamplesRef = useRef(0);
  const phaseRef = useRef<CapturePhase>("idle");
  const stopRecordingRef = useRef<() => void>(() => undefined);
  const sessionIdRef = useRef("");
  const ancEnabledRef = useRef(false);

  useEffect(() => {
    ancEnabledRef.current = ancEnabled;
  }, [ancEnabled]);

  useEffect(() => {
    phaseRef.current = phase;
  }, [phase]);

  const teardownAudio = useCallback(() => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    processorRef.current?.disconnect();
    processorRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    if (audioCtxRef.current?.state !== "closed") {
      void audioCtxRef.current?.close();
    }
    audioCtxRef.current = null;
    setAnalyser(null);
  }, []);

  const closeWs = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const scheduleMonitorChunk = useCallback((samples: Float32Array) => {
    const ctx = audioCtxRef.current;
    if (!ctx || !ancEnabledRef.current) return;
    const buffer = ctx.createBuffer(1, samples.length, TARGET_SAMPLE_RATE);
    buffer.getChannelData(0).set(samples);
    const src = ctx.createBufferSource();
    src.buffer = buffer;
    src.connect(ctx.destination);
    const startAt = Math.max(ctx.currentTime + 0.05, monitorTimeRef.current);
    src.start(startAt);
    monitorTimeRef.current = startAt + buffer.duration;
    setOutputLevel(rmsLevel(samples));
  }, []);

  const sendChunk = useCallback(
    (chunk: Float32Array) => {
      const ws = wsRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      if (pendingRef.current >= MAX_PENDING_CHUNKS) {
        setAncDegraded(true);
        return;
      }
      pendingRef.current += 1;
      const pcm = float32ToPcmB64(chunk);
      ws.send(
        JSON.stringify({
          type: "chunk",
          seq: seqRef.current,
          pcm,
          preview_method: "omlsa_preview",
        }),
      );
      seqRef.current += 1;
    },
    [],
  );

  const armMic = useCallback(async () => {
    setMicError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
        },
      });
      streamRef.current = stream;
      const ctx = new AudioContext();
      audioCtxRef.current = ctx;
      const source = ctx.createMediaStreamSource(stream);
      const analyserNode = ctx.createAnalyser();
      analyserNode.fftSize = 2048;
      source.connect(analyserNode);

      const processor = ctx.createScriptProcessor(4096, 1, 1);
      processor.onaudioprocess = (ev) => {
        const input = ev.inputBuffer.getChannelData(0);
        const copy = new Float32Array(input.length);
        copy.set(input);
        const down = downsampleTo16k(copy, ctx.sampleRate);
        const rms = rmsLevel(down);
        setInputLevel(rms);
        setLevelDb(20 * Math.log10(Math.max(rms, 1e-6)));

        if (phaseRef.current !== "recording") return;

        const prev = bufferRef.current;
        const merged = new Float32Array(prev.length + down.length);
        merged.set(prev);
        merged.set(down, prev.length);
        bufferRef.current = merged;

        while (bufferRef.current.length >= CHUNK_SAMPLES) {
          const chunk = bufferRef.current.slice(0, CHUNK_SAMPLES);
          bufferRef.current = bufferRef.current.slice(CHUNK_SAMPLES);
          sendChunk(chunk);
        }

        totalSamplesRef.current += down.length;
        if (totalSamplesRef.current / TARGET_SAMPLE_RATE >= MAX_RECORD_SEC) {
          stopRecordingRef.current();
        }
      };
      source.connect(processor);
      processor.connect(ctx.destination);
      processorRef.current = processor;
      setAnalyser(analyserNode);
      return true;
    } catch {
      setMicError("recordMicDenied");
      return false;
    }
  }, [sendChunk]);

  const startRecording = useCallback(async () => {
    setMicError("");
    setPreviewUrls(null);
    setAncDegraded(false);
    setPhase("arming");
    const ok = await armMic();
    if (!ok) {
      setPhase("idle");
      return;
    }

    await new Promise((r) => window.setTimeout(r, 800));
    try {
      const session = await createRecordSession();
      sessionIdRef.current = session.session_id;
      setSessionId(session.session_id);
      seqRef.current = 0;
      pendingRef.current = 0;
      bufferRef.current = new Float32Array(0);
      totalSamplesRef.current = 0;
      monitorTimeRef.current = audioCtxRef.current?.currentTime ?? 0;

      const ws = new WebSocket(recordStreamUrl(session.session_id));
      wsRef.current = ws;
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data as string) as {
            type: string;
            pcm?: string;
            latency_ms?: number;
            code?: string;
            message?: string;
          };
          if (msg.type === "denoised" && msg.pcm) {
            pendingRef.current = Math.max(0, pendingRef.current - 1);
            if (msg.latency_ms != null) setLatencyMs(msg.latency_ms);
            scheduleMonitorChunk(pcmB64ToFloat32(msg.pcm));
          } else if (msg.type === "error") {
            setMicError(msg.message ?? "error");
          }
        } catch {
          /* ignore */
        }
      };

      await new Promise<void>((resolve, reject) => {
        const t = window.setTimeout(() => reject(new Error("ws timeout")), 5000);
        ws.onopen = () => {
          window.clearTimeout(t);
          resolve();
        };
        ws.onerror = () => {
          window.clearTimeout(t);
          reject(new Error("ws error"));
        };
      });

      setPhase("recording");
      setTimerSec(0);
      timerRef.current = window.setInterval(() => {
        setTimerSec((s) => s + 1);
      }, 1000);
    } catch (e) {
      setMicError(String(e));
      setPhase("idle");
      closeWs();
    }
  }, [armMic, closeWs, scheduleMonitorChunk]);

  const stopRecording = useCallback(async () => {
    if (phaseRef.current !== "recording") return;
    setPhase("preview");

    if (bufferRef.current.length > 0) {
      sendChunk(bufferRef.current);
      bufferRef.current = new Float32Array(0);
    }

    closeWs();

    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }

    const sid = sessionIdRef.current;
    if (sid) {
      try {
        await finishRecordSession(sid);
        setPreviewUrls({
          raw: recordAudioUrl(sid, "raw"),
          preview: recordAudioUrl(sid, "preview"),
        });
      } catch (e) {
        setMicError(String(e));
      }
    }
  }, [sendChunk, closeWs]);

  useEffect(() => {
    stopRecordingRef.current = () => {
      void stopRecording();
    };
  }, [stopRecording]);

  const retake = useCallback(() => {
    closeWs();
    teardownAudio();
    sessionIdRef.current = "";
    setSessionId("");
    setPreviewUrls(null);
    setTimerSec(0);
    setPhase("idle");
    setAncEnabled(false);
    setAncDegraded(false);
  }, [closeWs, teardownAudio]);

  const commitTask = useCallback(
    async (req: Omit<ProcessRequest, "task_id">) => {
      if (!sessionId) return null;
      setPhase("committing");
      try {
        const res = await commitRecordSession(sessionId, req);
        return res.task_id;
      } catch (e) {
        setMicError(String(e));
        setPhase("preview");
        return null;
      }
    },
    [sessionId],
  );

  useEffect(() => {
    return () => {
      closeWs();
      teardownAudio();
    };
  }, [closeWs, teardownAudio]);

  return {
    phase,
    sessionId,
    timerSec,
    inputLevel,
    outputLevel,
    levelDb,
    latencyMs,
    ancEnabled,
    setAncEnabled,
    ancDegraded,
    micError,
    previewUrls,
    analyser,
    armMic,
    startRecording,
    stopRecording,
    retake,
    commitTask,
  };
}
