export interface DetectedMiner {
  id: number;
  ipAddress: string;
  macAddress?: string;
  hostname?: string;
  latitude?: number;
  longitude?: number;
  city?: string;
  detectionMethod: string;
  powerConsumption?: number;
  hashRate?: string;
  deviceType?: string;
  processName?: string;
  cpuUsage?: number;
  memoryUsage?: number;
  networkUsage?: number;
  gpuUsage?: number;
  detectionTime: string;
  confidenceScore: number;
  threatLevel: 'low' | 'medium' | 'high';
  notes?: string;
  isActive?: boolean;
}

export interface NetworkConnection {
  id: number;
  localAddress: string;
  localPort: number;
  remoteAddress?: string;
  remotePort?: number;
  protocol: string;
  status: string;
  processName?: string;
  detectionTime: string;
  minerId?: number;
}

export interface ScanSession {
  id: number;
  sessionType: string;
  ipRange?: string;
  ports?: string;
  startTime: string;
  endTime?: string;
  status: 'running' | 'completed' | 'failed';
  devicesFound: number;
  minersDetected: number;
  errors?: string;
}

export interface SystemActivity {
  id: number;
  activityType: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
  timestamp: string;
  metadata?: string;
}

export interface Statistics {
  totalDevices: number;
  confirmedMiners: number;
  suspiciousDevices: number;
  totalPowerConsumption: number;
  networkHealth: number;
}

export interface GeolocationData {
  ip: string;
  status: string;
  latitude?: number;
  longitude?: number;
  city?: string;
  region?: string;
  country?: string;
  in_ilam?: boolean;
  closest_ilam_city?: string;
  distance_to_city?: number;
  accuracy?: string;
  service?: string;
}

export interface ScanConfig {
  ipRange: string;
  ports: number[] | string;
  timeout?: number;
}

export interface WebSocketMessage {
  type: 'miner_detected' | 'miner_updated' | 'scan_started' | 'scan_progress' | 'scan_completed' | 'scan_failed' | 'network_scan_completed';
  data: any;
}
