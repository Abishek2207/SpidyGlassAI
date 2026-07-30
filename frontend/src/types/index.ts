export interface SystemTelemetry {
  fps: number;
  gpu_utilization: number;
  cpu_utilization?: number;
  ram_utilization?: number;
  battery: number;
  latency_ms: number;
}

export interface AgentTelemetry {
  status: 'idle' | 'active' | 'listening' | 'processing' | 'error' | 'online';
  confidence: number;
  latency_ms: number;
  task?: string;
  last_update?: number;
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

export interface DetectedObject {
  label: string;
  confidence: number;
  bbox: [number, number, number, number];
}

export interface DetectedFace {
  confidence: number;
  bbox: [number, number, number, number];
}

export interface FrameResult {
  image: string | null;
  gesture: { gesture: string; confidence: number } | null;
  objects?: DetectedObject[];
  faces?: DetectedFace[];
  process_time_ms: number;
}
