import { DetectedMiner, GeolocationData } from '@/lib/types';

// Ilam province boundaries
export const ILAM_BOUNDS = {
  north: 34.5,
  south: 32.0,
  east: 48.5,
  west: 45.5,
  center: [33.63, 46.42] as [number, number]
};

// Ilam cities with coordinates
export const ILAM_CITIES = {
  'ایلام': [33.6374, 46.4227] as [number, number],
  'مهران': [33.1221, 46.1641] as [number, number],
  'دهلران': [32.6942, 47.2678] as [number, number],
  'آبدانان': [32.9928, 47.4164] as [number, number],
  'دره‌شهر': [33.1458, 47.3667] as [number, number],
  'ایوان': [33.8081, 46.2892] as [number, number],
  'چرداول': [33.7333, 46.8833] as [number, number],
  'بدره': [33.0833, 47.1167] as [number, number],
  'سرابله': [32.9667, 46.5833] as [number, number],
  'ملکشاهی': [33.3833, 46.5667] as [number, number],
  'شیروان چرداول': [33.9, 46.95] as [number, number]
};

export function getThreatLevelColor(threatLevel: string): string {
  switch (threatLevel) {
    case 'high':
      return '#ef4444'; // red-500
    case 'medium':
      return '#f59e0b'; // amber-500
    case 'low':
      return '#10b981'; // emerald-500
    default:
      return '#6b7280'; // gray-500
  }
}

export function getThreatLevelIcon(threatLevel: string): string {
  switch (threatLevel) {
    case 'high':
      return '⚠️';
    case 'medium':
      return '⚡';
    case 'low':
      return '✅';
    default:
      return '❓';
  }
}

export function getDeviceTypeIcon(deviceType: string): string {
  const type = deviceType?.toLowerCase() || '';
  if (type.includes('antminer') || type.includes('whatsminer') || type.includes('asic')) {
    return '⛏️';
  }
  if (type.includes('gpu') || type.includes('graphics')) {
    return '🎮';
  }
  if (type.includes('cpu')) {
    return '💻';
  }
  return '🔧';
}

export function isInIlamBounds(lat: number, lon: number): boolean {
  return (
    lat >= ILAM_BOUNDS.south &&
    lat <= ILAM_BOUNDS.north &&
    lon >= ILAM_BOUNDS.west &&
    lon <= ILAM_BOUNDS.east
  );
}

export function findClosestCity(lat: number, lon: number): { city: string; distance: number } {
  let closestCity = 'ایلام';
  let minDistance = Infinity;

  Object.entries(ILAM_CITIES).forEach(([city, [cityLat, cityLon]]) => {
    const distance = calculateDistance(lat, lon, cityLat, cityLon);
    if (distance < minDistance) {
      minDistance = distance;
      closestCity = city;
    }
  });

  return { city: closestCity, distance: minDistance };
}

export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth's radius in kilometers
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

export function formatHashRate(hashRate: string | null | undefined): string {
  if (!hashRate) return 'نامشخص';
  return hashRate;
}

export function formatPowerConsumption(power: number | null | undefined): string {
  if (!power) return 'نامشخص';
  if (power >= 1000) {
    return `${(power / 1000).toFixed(1)} کیلووات`;
  }
  return `${power.toFixed(0)} وات`;
}

export function formatConfidenceScore(score: number): string {
  return `${score}%`;
}
