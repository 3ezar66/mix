import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { 
  MapPin, 
  Search, 
  Filter, 
  Layers, 
  Navigation, 
  Target, 
  Eye, 
  EyeOff,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Download,
  Share,
  Info,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Radio,
  Volume2,
  Thermometer,
  Building2,
  Car,
  User,
  Phone,
  Mail,
  Map,
  Satellite,
  Globe,
  Compass,
  Crosshair,
  Maximize2,
  Minimize2,
  Settings,
  BarChart3,
  PieChart,
  TrendingUp,
  Layers3,
  Grid3X3,
  Circle,
  Square,
  Triangle,
  Star
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

interface MapDevice {
  id: string;
  ipAddress: string;
  macAddress: string;
  location: {
    latitude: number;
    longitude: number;
    address: string;
    city: string;
    region: string;
    district: string;
    street: string;
    building: string;
    floor: string;
    room: string;
  };
  owner: {
    name: string;
    phone: string;
    nationalId: string;
    address: string;
    verificationStatus: string;
    familyMembers: string[];
    contactInfo: {
      email: string;
      emergencyContact: string;
      workPhone: string;
    };
  };
  deviceInfo: {
    type: string;
    model: string;
    manufacturer: string;
    serialNumber: string;
    powerConsumption: number;
    hashRate: string;
    algorithm: string;
    temperature: number;
    uptime: string;
    lastSeen: string;
  };
  detectionInfo: {
    methods: string[];
    confidenceScore: number;
    threatLevel: 'low' | 'medium' | 'high' | 'critical';
    firstDetected: string;
    lastDetected: string;
    detectionCount: number;
    status: 'active' | 'inactive' | 'investigating' | 'resolved';
  };
  networkInfo: {
    subnet: string;
    gateway: string;
    dns: string[];
    openPorts: number[];
    services: string[];
    bandwidth: number;
    latency: number;
  };
  rfInfo: {
    frequency: number;
    signalStrength: number;
    modulation: string;
    bandwidth: number;
    interference: boolean;
  };
  acousticInfo: {
    signature: string;
    decibelLevel: number;
    frequency: number;
    pattern: string;
  };
  thermalInfo: {
    surfaceTemp: number;
    ambientTemp: number;
    heatSignature: string;
    coolingSystem: string;
  };
}

interface MapLayer {
  id: string;
  name: string;
  visible: boolean;
  opacity: number;
  color: string;
  icon: string;
}

interface MapFilter {
  threatLevel: string[];
  status: string[];
  deviceType: string[];
  city: string[];
  detectionMethod: string[];
  powerConsumption: {
    min: number;
    max: number;
  };
  confidenceScore: {
    min: number;
    max: number;
  };
}

const AdvancedInteractiveMap: React.FC = () => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [selectedDevice, setSelectedDevice] = useState<MapDevice | null>(null);
  const [mapLayers, setMapLayers] = useState<MapLayer[]>([
    { id: 'miners', name: 'ماینرها', visible: true, opacity: 1, color: '#ef4444', icon: 'Zap' },
    { id: 'suspicious', name: 'مشکوک', visible: true, opacity: 0.8, color: '#f59e0b', icon: 'AlertTriangle' },
    { id: 'investigating', name: 'در حال بررسی', visible: true, opacity: 0.9, color: '#3b82f6', icon: 'Clock' },
    { id: 'resolved', name: 'حل شده', visible: false, opacity: 0.6, color: '#10b981', icon: 'CheckCircle' },
    { id: 'heatmap', name: 'نقشه حرارتی', visible: false, opacity: 0.7, color: '#ff6b6b', icon: 'Thermometer' },
    { id: 'rf_signals', name: 'سیگنال‌های RF', visible: false, opacity: 0.8, color: '#8b5cf6', icon: 'Radio' },
    { id: 'acoustic', name: 'امضاهای صوتی', visible: false, opacity: 0.8, color: '#06b6d4', icon: 'Volume2' },
    { id: 'network', name: 'شبکه', visible: false, opacity: 0.6, color: '#84cc16', icon: 'Network' }
  ]);
  
  const [mapFilters, setMapFilters] = useState<MapFilter>({
    threatLevel: [],
    status: [],
    deviceType: [],
    city: [],
    detectionMethod: [],
    powerConsumption: { min: 0, max: 10000 },
    confidenceScore: { min: 0, max: 100 }
  });
  
  const [mapView, setMapView] = useState({
    center: { lat: 33.6374, lng: 46.4227 }, // Ilam coordinates
    zoom: 12,
    bearing: 0,
    pitch: 0
  });
  
  const [searchQuery, setSearchQuery] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showClusters, setShowClusters] = useState(true);
  const [showLabels, setShowLabels] = useState(true);

  // Fetch map data
  const { data: mapDevices, isLoading } = useQuery<MapDevice[]>({
    queryKey: ['map-devices', mapFilters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (mapFilters.threatLevel.length > 0) {
        params.append('threat_level', mapFilters.threatLevel.join(','));
      }
      if (mapFilters.status.length > 0) {
        params.append('status', mapFilters.status.join(','));
      }
      if (mapFilters.city.length > 0) {
        params.append('city', mapFilters.city.join(','));
      }
      
      const response = await axios.get(`/api/v2/map/devices?${params.toString()}`);
      return response.data;
    },
    refetchInterval: 30000
  });

  // Filter devices based on search and filters
  const filteredDevices = mapDevices?.filter(device => {
    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      const matches = 
        device.ipAddress.toLowerCase().includes(query) ||
        device.owner.name.toLowerCase().includes(query) ||
        device.location.address.toLowerCase().includes(query) ||
        device.location.city.toLowerCase().includes(query);
      
      if (!matches) return false;
    }
    
    // Threat level filter
    if (mapFilters.threatLevel.length > 0 && !mapFilters.threatLevel.includes(device.detectionInfo.threatLevel)) {
      return false;
    }
    
    // Status filter
    if (mapFilters.status.length > 0 && !mapFilters.status.includes(device.detectionInfo.status)) {
      return false;
    }
    
    // Device type filter
    if (mapFilters.deviceType.length > 0 && !mapFilters.deviceType.includes(device.deviceInfo.type)) {
      return false;
    }
    
    // City filter
    if (mapFilters.city.length > 0 && !mapFilters.city.includes(device.location.city)) {
      return false;
    }
    
    // Detection method filter
    if (mapFilters.detectionMethod.length > 0) {
      const hasMatchingMethod = device.detectionInfo.methods.some(method => 
        mapFilters.detectionMethod.includes(method)
      );
      if (!hasMatchingMethod) return false;
    }
    
    // Power consumption filter
    if (device.deviceInfo.powerConsumption < mapFilters.powerConsumption.min || 
        device.deviceInfo.powerConsumption > mapFilters.powerConsumption.max) {
      return false;
    }
    
    // Confidence score filter
    if (device.detectionInfo.confidenceScore < mapFilters.confidenceScore.min || 
        device.detectionInfo.confidenceScore > mapFilters.confidenceScore.max) {
      return false;
    }
    
    return true;
  }) || [];

  const getDeviceIcon = (device: MapDevice) => {
    switch (device.detectionInfo.threatLevel) {
      case 'critical': return <Star className="w-6 h-6 text-red-600" />;
      case 'high': return <Triangle className="w-6 h-6 text-orange-500" />;
      case 'medium': return <Square className="w-6 h-6 text-yellow-500" />;
      case 'low': return <Circle className="w-6 h-6 text-green-500" />;
      default: return <Circle className="w-6 h-6 text-gray-500" />;
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600';
      case 'inactive': return 'text-gray-600';
      case 'investigating': return 'text-blue-600';
      case 'resolved': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  };

  const handleDeviceClick = (device: MapDevice) => {
    setSelectedDevice(device);
  };

  const handleLayerToggle = (layerId: string) => {
    setMapLayers(prev => prev.map(layer => 
      layer.id === layerId ? { ...layer, visible: !layer.visible } : layer
    ));
  };

  const handleLayerOpacityChange = (layerId: string, opacity: number) => {
    setMapLayers(prev => prev.map(layer => 
      layer.id === layerId ? { ...layer, opacity } : layer
    ));
  };

  const handleMapViewChange = (newView: any) => {
    setMapView(newView);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleFilterChange = (filterType: keyof MapFilter, value: any) => {
    setMapFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const exportMapData = () => {
    const data = {
      devices: filteredDevices,
      filters: mapFilters,
      view: mapView,
      timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `map_data_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const shareMap = () => {
    const shareData = {
      title: 'نقشه ماینرهای غیرمجاز - استان ایلام',
      text: `تعداد ${filteredDevices.length} دستگاه در نقشه`,
      url: window.location.href
    };
    
    if (navigator.share) {
      navigator.share(shareData);
    } else {
      navigator.clipboard.writeText(window.location.href);
    }
  };

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50' : 'h-full'} bg-white`}>
      {/* Map Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-bold">نقشه تعاملی پیشرفته</h2>
          <Badge variant="outline">{filteredDevices.length} دستگاه</Badge>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={() => setShowHeatmap(!showHeatmap)}>
            <Thermometer className="w-4 h-4 mr-2" />
            نقشه حرارتی
          </Button>
          <Button variant="outline" size="sm" onClick={() => setShowClusters(!showClusters)}>
            <Grid3X3 className="w-4 h-4 mr-2" />
            خوشه‌بندی
          </Button>
          <Button variant="outline" size="sm" onClick={() => setShowLabels(!showLabels)}>
            {showLabels ? <EyeOff className="w-4 h-4 mr-2" /> : <Eye className="w-4 h-4 mr-2" />}
            برچسب‌ها
          </Button>
          <Button variant="outline" size="sm" onClick={exportMapData}>
            <Download className="w-4 h-4 mr-2" />
            خروجی
          </Button>
          <Button variant="outline" size="sm" onClick={shareMap}>
            <Share className="w-4 h-4 mr-2" />
            اشتراک
          </Button>
          <Button variant="outline" size="sm" onClick={() => setIsFullscreen(!isFullscreen)}>
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      <div className="flex h-full">
        {/* Sidebar */}
        <div className="w-80 border-r bg-gray-50 overflow-y-auto">
          {/* Search */}
          <div className="p-4 border-b">
            <Label htmlFor="search">جستجو</Label>
            <div className="relative mt-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                id="search"
                placeholder="جستجو بر اساس IP، نام یا آدرس..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="p-4 border-b">
            <h3 className="font-medium mb-3">فیلترها</h3>
            
            <div className="space-y-3">
              <div>
                <Label>سطح تهدید</Label>
                <Select 
                  value={mapFilters.threatLevel.join(',')} 
                  onValueChange={(value) => handleFilterChange('threatLevel', value ? value.split(',') : [])}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="انتخاب سطح تهدید" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="critical">بحرانی</SelectItem>
                    <SelectItem value="high">زیاد</SelectItem>
                    <SelectItem value="medium">متوسط</SelectItem>
                    <SelectItem value="low">کم</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>وضعیت</Label>
                <Select 
                  value={mapFilters.status.join(',')} 
                  onValueChange={(value) => handleFilterChange('status', value ? value.split(',') : [])}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="انتخاب وضعیت" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">فعال</SelectItem>
                    <SelectItem value="inactive">غیرفعال</SelectItem>
                    <SelectItem value="investigating">در حال بررسی</SelectItem>
                    <SelectItem value="resolved">حل شده</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>مصرف برق (وات)</Label>
                <div className="flex space-x-2">
                  <Input
                    type="number"
                    placeholder="حداقل"
                    value={mapFilters.powerConsumption.min}
                    onChange={(e) => handleFilterChange('powerConsumption', {
                      ...mapFilters.powerConsumption,
                      min: parseInt(e.target.value) || 0
                    })}
                  />
                  <Input
                    type="number"
                    placeholder="حداکثر"
                    value={mapFilters.powerConsumption.max}
                    onChange={(e) => handleFilterChange('powerConsumption', {
                      ...mapFilters.powerConsumption,
                      max: parseInt(e.target.value) || 10000
                    })}
                  />
                </div>
              </div>

              <div>
                <Label>امتیاز اطمینان (%)</Label>
                <div className="flex space-x-2">
                  <Input
                    type="number"
                    placeholder="حداقل"
                    value={mapFilters.confidenceScore.min}
                    onChange={(e) => handleFilterChange('confidenceScore', {
                      ...mapFilters.confidenceScore,
                      min: parseInt(e.target.value) || 0
                    })}
                  />
                  <Input
                    type="number"
                    placeholder="حداکثر"
                    value={mapFilters.confidenceScore.max}
                    onChange={(e) => handleFilterChange('confidenceScore', {
                      ...mapFilters.confidenceScore,
                      max: parseInt(e.target.value) || 100
                    })}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Layers */}
          <div className="p-4 border-b">
            <h3 className="font-medium mb-3">لایه‌ها</h3>
            <div className="space-y-2">
              {mapLayers.map((layer) => (
                <div key={layer.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={layer.visible}
                      onCheckedChange={() => handleLayerToggle(layer.id)}
                    />
                    <span className="text-sm">{layer.name}</span>
                  </div>
                  {layer.visible && (
                    <Slider
                      value={[layer.opacity * 100]}
                      onValueChange={([value]) => handleLayerOpacityChange(layer.id, value / 100)}
                      max={100}
                      step={10}
                      className="w-20"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Device List */}
          <div className="p-4">
            <h3 className="font-medium mb-3">دستگاه‌ها</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredDevices.map((device) => (
                <div
                  key={device.id}
                  className="p-3 border rounded-lg cursor-pointer hover:bg-gray-100"
                  onClick={() => handleDeviceClick(device)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">{device.ipAddress}</p>
                      <p className="text-xs text-gray-500">{device.location.address}</p>
                    </div>
                    <Badge className={getThreatLevelColor(device.detectionInfo.threatLevel)}>
                      {device.detectionInfo.threatLevel}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <p className="text-xs text-gray-500">{device.owner.name}</p>
                    <p className="text-xs text-gray-500">{device.deviceInfo.powerConsumption}W</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div className="flex-1 relative">
          <div ref={mapRef} className="w-full h-full bg-gray-100">
            {/* Map will be rendered here */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Map className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">نقشه در حال بارگذاری...</p>
              </div>
            </div>
          </div>

          {/* Map Controls */}
          <div className="absolute top-4 right-4 space-y-2">
            <Button size="sm" variant="outline" className="w-10 h-10 p-0">
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button size="sm" variant="outline" className="w-10 h-10 p-0">
              <ZoomOut className="w-4 h-4" />
            </Button>
            <Button size="sm" variant="outline" className="w-10 h-10 p-0">
              <RotateCcw className="w-4 h-4" />
            </Button>
            <Button size="sm" variant="outline" className="w-10 h-10 p-0">
              <Crosshair className="w-4 h-4" />
            </Button>
          </div>

          {/* Map Legend */}
          <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg">
            <h4 className="font-medium mb-2">راهنما</h4>
            <div className="space-y-1 text-sm">
              <div className="flex items-center space-x-2">
                <Star className="w-4 h-4 text-red-600" />
                <span>بحرانی</span>
              </div>
              <div className="flex items-center space-x-2">
                <Triangle className="w-4 h-4 text-orange-500" />
                <span>زیاد</span>
              </div>
              <div className="flex items-center space-x-2">
                <Square className="w-4 h-4 text-yellow-500" />
                <span>متوسط</span>
              </div>
              <div className="flex items-center space-x-2">
                <Circle className="w-4 h-4 text-green-500" />
                <span>کم</span>
              </div>
            </div>
          </div>
        </div>

        {/* Device Detail Panel */}
        {selectedDevice && (
          <div className="w-96 border-l bg-white overflow-y-auto">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">جزئیات دستگاه</h3>
                <Button variant="outline" size="sm" onClick={() => setSelectedDevice(null)}>
                  بستن
                </Button>
              </div>
            </div>

            <div className="p-4 space-y-6">
              {/* Basic Info */}
              <div>
                <h4 className="font-medium mb-2">اطلاعات پایه</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>IP:</span>
                    <span className="font-medium">{selectedDevice.ipAddress}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>MAC:</span>
                    <span className="font-medium">{selectedDevice.macAddress}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>نوع:</span>
                    <span className="font-medium">{selectedDevice.deviceInfo.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>مدل:</span>
                    <span className="font-medium">{selectedDevice.deviceInfo.model}</span>
                  </div>
                </div>
              </div>

              {/* Location */}
              <div>
                <h4 className="font-medium mb-2">موقعیت</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-500">آدرس:</span>
                    <p className="font-medium">{selectedDevice.location.address}</p>
                  </div>
                  <div className="flex justify-between">
                    <span>شهر:</span>
                    <span className="font-medium">{selectedDevice.location.city}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>منطقه:</span>
                    <span className="font-medium">{selectedDevice.location.region}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>محله:</span>
                    <span className="font-medium">{selectedDevice.location.district}</span>
                  </div>
                </div>
              </div>

              {/* Owner Info */}
              <div>
                <h4 className="font-medium mb-2">اطلاعات مالک</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>نام:</span>
                    <span className="font-medium">{selectedDevice.owner.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>تلفن:</span>
                    <span className="font-medium">{selectedDevice.owner.phone}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>کد ملی:</span>
                    <span className="font-medium">{selectedDevice.owner.nationalId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>وضعیت تأیید:</span>
                    <Badge variant={selectedDevice.owner.verificationStatus === 'verified' ? 'default' : 'secondary'}>
                      {selectedDevice.owner.verificationStatus}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Device Status */}
              <div>
                <h4 className="font-medium mb-2">وضعیت دستگاه</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>مصرف برق:</span>
                    <span className="font-medium">{selectedDevice.deviceInfo.powerConsumption} وات</span>
                  </div>
                  <div className="flex justify-between">
                    <span>نرخ هش:</span>
                    <span className="font-medium">{selectedDevice.deviceInfo.hashRate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>دما:</span>
                    <span className="font-medium">{selectedDevice.deviceInfo.temperature}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span>زمان کارکرد:</span>
                    <span className="font-medium">{selectedDevice.deviceInfo.uptime}</span>
                  </div>
                </div>
              </div>

              {/* Detection Info */}
              <div>
                <h4 className="font-medium mb-2">اطلاعات تشخیص</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>سطح تهدید:</span>
                    <Badge className={getThreatLevelColor(selectedDevice.detectionInfo.threatLevel)}>
                      {selectedDevice.detectionInfo.threatLevel}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>امتیاز اطمینان:</span>
                    <span className="font-medium">{selectedDevice.detectionInfo.confidenceScore}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>وضعیت:</span>
                    <span className={getStatusColor(selectedDevice.detectionInfo.status)}>
                      {selectedDevice.detectionInfo.status}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">روش‌های تشخیص:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedDevice.detectionInfo.methods.map((method) => (
                        <Badge key={method} variant="outline" className="text-xs">
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-2">
                <Button className="w-full">
                  <Navigation className="w-4 h-4 mr-2" />
                  مسیریابی
                </Button>
                <Button variant="outline" className="w-full">
                  <Phone className="w-4 h-4 mr-2" />
                  تماس با مالک
                </Button>
                <Button variant="outline" className="w-full">
                  <FileText className="w-4 h-4 mr-2" />
                  دانلود گزارش
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedInteractiveMap;