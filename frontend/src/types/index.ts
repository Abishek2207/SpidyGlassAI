export interface SystemTelemetry {
  fps: number;
  gpu_utilization: number;
  battery: number;
  latency_ms: number;
}

export interface AgentTelemetry {
  status: 'idle' | 'active' | 'listening' | 'processing' | 'error';
  confidence: number;
  latency_ms: number;
}

export interface TelemetryPayload {
  system: SystemTelemetry;
  agents: Record<string, AgentTelemetry>;
}

export interface BoundingBox {
  x: number;
  y: number;
  z: number;
  id: number;
}

export interface FrameResult {
  image: string | null;
  gesture: { gesture: string; confidence: number } | null;
  process_time_ms: number;
}
