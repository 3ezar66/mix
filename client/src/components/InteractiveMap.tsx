import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from '@/components/ui/button';
import { RotateCcw, Maximize2, Minimize2, MapPin as MapIcon, Loader2, AlertTriangle } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

interface MinerLocation {
  id: string;
  latitude: number;
  longitude: number;
  ip_address: string;
  confidence_score: number;
  owner: {
    name: string;
    type: string;
  };
  last_seen: string;
}

const ILAM_BOUNDS = {
  north: 34.3353,
  south: 32.4084,
  east: 48.0936,
  west: 45.2401,
  center: [33.6369, 46.4223] as [number, number]
};

const MAX_RETRIES = 3;
const RETRY_DELAY = 2000;
const REFRESH_INTERVAL = 15000; // 15 seconds

const InteractiveMap = () => {
  const [locations, setLocations] = useState<MinerLocation[]>([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [selectedMiner, setSelectedMiner] = useState<MinerLocation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const mapRef = useRef<any>(null);
  const retryCountRef = useRef(0);

  const fetchWithRetry = async (url: string): Promise<any> => {
    while (retryCountRef.current < MAX_RETRIES) {
      try {
        const response = await fetch(url, {
          credentials: 'include',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }

        const data = await response.json();
        retryCountRef.current = 0;
        return data;
      } catch (error) {
        retryCountRef.current++;
        if (retryCountRef.current === MAX_RETRIES) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * retryCountRef.current));
      }
    }
  };

  const validateLocation = (location: MinerLocation): boolean => {
    return (
      location.latitude >= ILAM_BOUNDS.south &&
      location.latitude <= ILAM_BOUNDS.north &&
      location.longitude >= ILAM_BOUNDS.west &&
      location.longitude <= ILAM_BOUNDS.east
    );
  };

  useEffect(() => {
    const fetchLocations = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchWithRetry('/api/miners');
        
        // فیلتر کردن موقعیت‌های خارج از محدوده استان ایلام
        const validLocations = data.filter(validateLocation);
        
        setLocations(validLocations);
      } catch (error) {
        setError('خطا در دریافت اطلاعات موقعیت‌ها');
        console.error('Error fetching locations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLocations();
    const interval = setInterval(fetchLocations, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  const getMarkerColor = (score: number) => {
    if (score >= 90) return '#dc2626'; // قرمز تیره برای اطمینان بسیار بالا
    if (score >= 80) return '#ef4444'; // قرمز برای اطمینان بالا
    if (score >= 70) return '#f97316'; // نارنجی برای اطمینان متوسط به بالا
    if (score >= 60) return '#eab308'; // زرد برای اطمینان متوسط
    if (score >= 40) return '#22c55e'; // سبز برای اطمینان کم
    return '#71717a'; // خاکستری برای اطمینان خیلی کم
  };

  const getMarkerSize = (score: number): number => {
    if (score >= 80) return 12;
    if (score >= 60) return 10;
    return 8;
  };

  const formatLastSeen = (date: string): string => {
    const lastSeen = new Date(date);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - lastSeen.getTime()) / 60000);
    
    if (diffMinutes < 60) {
      return `${diffMinutes} دقیقه پیش`;
    } else if (diffMinutes < 1440) {
      return `${Math.floor(diffMinutes / 60)} ساعت پیش`;
    } else {
      return lastSeen.toLocaleDateString('fa-IR');
    }
  };

  const handleRefresh = () => {
    if (mapRef.current) {
      mapRef.current.setView([33.6369, 46.4223], 8);
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    
    setTimeout(() => {
      if (mapRef.current) {
        mapRef.current.invalidateSize();
      }
    }, 100);
  };

  return (
    <Card className={`persian-card mb-6 ${isFullscreen ? 'fixed inset-4 z-50' : ''}`}>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center text-lg">
            <MapIcon className="ml-2 h-5 w-5 text-primary" />
            نقشه توزیع ماینرها - استان ایلام
          </CardTitle>
          <div className="flex space-x-reverse space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              className="focus-ring"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleFullscreen}
              className="focus-ring"
            >
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading && (
          <div className="absolute inset-0 bg-background/50 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="flex flex-col items-center space-y-2">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">در حال بارگذاری اطلاعات...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-4 p-4 bg-persian-error/10 border border-persian-error/20 rounded-lg text-persian-error">
            <div className="flex items-center space-x-2 space-x-reverse">
              <AlertTriangle className="h-5 w-5" />
              <p>{error}</p>
            </div>
          </div>
        )}

        <div className={`map-container ${isFullscreen ? 'h-[calc(100vh-8rem)]' : 'h-96'} relative overflow-hidden rounded-lg`}>
          <MapContainer
            center={[33.6369, 46.4223]} // Center on Ilam Province
            zoom={8}
            scrollWheelZoom={true}
            className="h-full w-full"
            ref={mapRef}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {locations.map((location) => (
              <CircleMarker
                key={location.id}
                center={[location.latitude, location.longitude]}
                radius={getMarkerSize(location.confidence_score)}
                eventHandlers={{
                  click: () => setSelectedMiner(location),
                }}
                pathOptions={{
                  fillColor: getMarkerColor(location.confidence_score),
                  color: getMarkerColor(location.confidence_score),
                  fillOpacity: 0.7,
                  weight: 2
                }}
              >
                <Popup>
                  <div className="p-2 min-w-[200px]">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-bold text-sm">{location.ip_address}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        location.confidence_score >= 80 ? 'bg-persian-error/10 text-persian-error' :
                        location.confidence_score >= 60 ? 'bg-persian-warning/10 text-persian-warning' :
                        'bg-persian-success/10 text-persian-success'
                      }`}>
                        {location.confidence_score}% اطمینان
                      </span>
                    </div>
                    <div className="space-y-1 text-sm">
                      <p className="flex justify-between">
                        <span className="text-muted-foreground">مالک:</span>
                        <span className="font-medium">{location.owner.name}</span>
                      </p>
                      <p className="flex justify-between">
                        <span className="text-muted-foreground">نوع:</span>
                        <span className="font-medium">{location.owner.type}</span>
                      </p>
                      <p className="flex justify-between">
                        <span className="text-muted-foreground">آخرین مشاهده:</span>
                        <span className="font-medium">{formatLastSeen(location.last_seen)}</span>
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-3"
                      onClick={() => setSelectedMiner(location)}
                    >
                      نمایش جزئیات بیشتر
                    </Button>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        {/* Selected Miner Info */}
        {selectedMiner && (
          <div className="mt-4 p-4 bg-persian-surface-variant rounded-lg border border-border">
            <div className="flex justify-between items-start mb-3">
              <h4 className="font-semibold text-foreground">اطلاعات دستگاه انتخابی</h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedMiner(null)}
                className="h-6 w-6 p-0"
              >
                ×
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">IP:</span>
                <span className="mr-2 font-medium">{selectedMiner.ip_address}</span>
              </div>
              <div>
                <span className="text-muted-foreground">امتیاز شک:</span>
                <span className="mr-2 font-medium">{selectedMiner.confidence_score}</span>
              </div>
              <div>
                <span className="text-muted-foreground">نوع:</span>
                <span className="mr-2 font-medium">{selectedMiner.owner.type}</span>
              </div>
              <div>
                <span className="text-muted-foreground">شهر:</span>
                <span className="mr-2 font-medium">{selectedMiner.owner.name}</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default InteractiveMap;
