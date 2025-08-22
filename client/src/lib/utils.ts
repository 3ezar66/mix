import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function formatHashRate(hashes: number): string {
  if (hashes === 0) return "0 H/s";
  const k = 1000;
  const sizes = ["H/s", "KH/s", "MH/s", "GH/s", "TH/s"];
  const i = Math.floor(Math.log(hashes) / Math.log(k));
  return `${parseFloat((hashes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function formatPower(watts: number): string {
  if (watts < 1000) return `${watts.toFixed(1)} W`;
  return `${(watts / 1000).toFixed(2)} kW`;
}

export function getConfidenceLevel(score: number): string {
  if (score >= 80) return "High";
  if (score >= 60) return "Medium";
  return "Low";
}

export function isValidIPRange(range: string): boolean {
  const parts = range.split("-");
  if (parts.length !== 2) return false;

  const [start, end] = parts;
  const startIP = start.split(".");
  const endIP = end.split(".");

  if (startIP.length !== 4 || endIP.length !== 4) return false;

  for (const part of [...startIP, ...endIP]) {
    const num = parseInt(part);
    if (isNaN(num) || num < 0 || num > 255) return false;
  }

  return true;
}

export function isValidPortRange(range: string): boolean {
  const parts = range.split("-");
  if (parts.length !== 2) return false;

  const [start, end] = parts;
  const startPort = parseInt(start);
  const endPort = parseInt(end);

  if (isNaN(startPort) || isNaN(endPort)) return false;
  if (startPort < 1 || startPort > 65535) return false;
  if (endPort < 1 || endPort > 65535) return false;
  if (startPort > endPort) return false;

  return true;
}
