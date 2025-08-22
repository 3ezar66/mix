import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  MapPin, 
  Shield, 
  Target, 
  TrendingUp, 
  Users, 
  Wifi,
  Zap,
  Database,
  Cpu,
  HardDrive,
  Network,
  BarChart3,
  Settings,
  Bell,
  Eye,
  Search
} from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useToast } from '../hooks/use-toast';

interface DetectionResult {
  id: string;
  timestamp: string;
  ip_address: string;
  mac_address?: string;
  location: { lat: number; lng: number };
  confidence: number;
  miner_type: string;
  scan_type: string;
  status: string;
  details: any;
  owner_info?: any;
}

interface SystemMetrics {
  total_detections: number;
  active_scans: number;
  system_status: string;
  last_scan_time?: string;
  detection_rate: number;
  false_positive_rate: number;
  coverage_percentage: number;
}

interface Alert {
  id: string;
  timestamp: string;
  type: string;
  severity: string;
  message: string;
  details: any;
  resolved: boolean;
}

interface AdvancedDashboardProps {
  className?: string;
}

export const AdvancedDashboard: React.FC<AdvancedDashboardProps> = ({ className }) => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [detections, setDetections] = useState<DetectionResult[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [scanStatus, setScanStatus] = useState<'idle' | 'scanning' | 'completed'>('idle');
  
  const { toast } = useToast();
  const { sendMessage, lastMessage, connectionStatus } = useWebSocket();

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        handleWebSocketMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Load metrics
      const metricsResponse = await fetch('/api/v2/dashboard/metrics');
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setMetrics(metricsData);
      }

      // Load recent detections
      const detectionsResponse = await fetch('/api/v2/detections/recent');
      if (detectionsResponse.ok) {
        const detectionsData = await detectionsResponse.json();
        setDetections(detectionsData);
      }

      // Load alerts
      const alertsResponse = await fetch('/api/v2/alerts/recent');
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast({
        title: "خطا",
        description: "خطا در بارگذاری داده‌های داشبورد",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'metrics_update':
        setMetrics(data.metrics);
        break;
      case 'new_detection':
        setDetections(prev => [data.detection, ...prev.slice(0, 49)]);
        toast({
          title: "تشخیص جدید",
          description: `ماینر جدید در ${data.detection.ip_address} شناسایی شد`,
        });
        break;
      case 'new_alert':
        setAlerts(prev => [data.alert, ...prev.slice(0, 19)]);
        toast({
          title: "هشدار جدید",
          description: data.alert.message,
          variant: data.alert.severity === 'high' ? 'destructive' : 'default'
        });
        break;
      case 'scan_status':
        setScanStatus(data.status);
        break;
    }
  };

  const startScan = async (scanType: string) => {
    try {
      setScanStatus('scanning');
      const response = await fetch('/api/v2/scan/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scan_type: scanType })
      });
      
      if (response.ok) {
        toast({
          title: "شروع اسکن",
          description: `اسکن ${scanType} شروع شد`,
        });
      }
    } catch (error) {
      console.error('Failed to start scan:', error);
      setScanStatus('idle');
      toast({
        title: "خطا",
        description: "خطا در شروع اسکن",
        variant: "destructive"
      });
    }
  };

  const stopScan = async () => {
    try {
      const response = await fetch('/api/v2/scan/stop', { method: 'POST' });
      if (response.ok) {
        setScanStatus('completed');
        toast({
          title: "توقف اسکن",
          description: "اسکن متوقف شد",
        });
      }
    } catch (error) {
      console.error('Failed to stop scan:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">داشبورد پیشرفته</h1>
          <p className="text-muted-foreground">سیستم ملی تشخیص ماینینگ غیرمجاز</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={connectionStatus === 'Connected' ? 'default' : 'destructive'}>
            {connectionStatus === 'Connected' ? 'متصل' : 'قطع اتصال'}
          </Badge>
          <Button onClick={loadDashboardData} variant="outline" size="sm">
            <BarChart3 className="h-4 w-4 mr-2" />
            به‌روزرسانی
          </Button>
        </div>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            وضعیت سیستم
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(metrics?.system_status || 'unknown')}`}></div>
              <span>وضعیت: {metrics?.system_status || 'نامشخص'}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Wifi className="h-4 w-4" />
              <span>اسکن‌های فعال: {metrics?.active_scans || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Target className="h-4 w-4" />
              <span>تشخیص‌ها: {metrics?.total_detections || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4" />
              <span>نرخ تشخیص: {metrics?.detection_rate?.toFixed(2) || 0}/ساعت</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">نمای کلی</TabsTrigger>
          <TabsTrigger value="detections">تشخیص‌ها</TabsTrigger>
          <TabsTrigger value="alerts">هشدارها</TabsTrigger>
          <TabsTrigger value="controls">کنترل‌ها</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Coverage Progress */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">پوشش منطقه</CardTitle>
                <MapPin className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics?.coverage_percentage?.toFixed(1) || 0}%</div>
                <Progress value={metrics?.coverage_percentage || 0} className="mt-2" />
              </CardContent>
            </Card>

            {/* False Positive Rate */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">نرخ خطای مثبت</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{(metrics?.false_positive_rate || 0) * 100}%</div>
                <p className="text-xs text-muted-foreground">آخرین 24 ساعت</p>
              </CardContent>
            </Card>

            {/* Active Users */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">کاربران فعال</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-muted-foreground">+2 از دیروز</p>
              </CardContent>
            </Card>

            {/* System Uptime */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">زمان کارکرد</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24h 15m</div>
                <p className="text-xs text-muted-foreground">آخرین راه‌اندازی</p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>فعالیت‌های اخیر</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {detections.slice(0, 5).map((detection) => (
                  <div key={detection.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <div>
                        <p className="font-medium">{detection.ip_address}</p>
                        <p className="text-sm text-muted-foreground">
                          {detection.miner_type} - {detection.scan_type}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">{detection.confidence}%</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(detection.timestamp).toLocaleString('fa-IR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="detections" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>تشخیص‌های اخیر</span>
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4 mr-2" />
                  مشاهده همه
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {detections.map((detection) => (
                  <div key={detection.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Badge variant="destructive">{detection.miner_type}</Badge>
                        <Badge variant="outline">{detection.scan_type}</Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(detection.timestamp).toLocaleString('fa-IR')}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium">IP:</span> {detection.ip_address}
                      </div>
                      <div>
                        <span className="font-medium">MAC:</span> {detection.mac_address || 'نامشخص'}
                      </div>
                      <div>
                        <span className="font-medium">اطمینان:</span> {detection.confidence}%
                      </div>
                      <div>
                        <span className="font-medium">وضعیت:</span> {detection.status}
                      </div>
                    </div>
                    {detection.owner_info && (
                      <div className="mt-2 p-2 bg-muted rounded text-sm">
                        <span className="font-medium">اطلاعات مالک:</span> {detection.owner_info.name || 'نامشخص'}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>هشدارهای سیستم</span>
                <Button variant="outline" size="sm">
                  <Bell className="h-4 w-4 mr-2" />
                  تنظیمات هشدار
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alerts.map((alert) => (
                  <Alert key={alert.id} variant={alert.severity === 'high' ? 'destructive' : 'default'}>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <div className="flex items-center justify-between">
                        <span>{alert.message}</span>
                        <Badge variant="outline" className="ml-2">
                          {alert.severity}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(alert.timestamp).toLocaleString('fa-IR')}
                      </p>
                    </AlertDescription>
                  </Alert>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="controls" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>کنترل‌های اسکن</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Button 
                  onClick={() => startScan('network')}
                  disabled={scanStatus === 'scanning'}
                  className="h-20 flex flex-col items-center justify-center"
                >
                  <Network className="h-6 w-6 mb-2" />
                  اسکن شبکه
                </Button>
                
                <Button 
                  onClick={() => startScan('rf')}
                  disabled={scanStatus === 'scanning'}
                  className="h-20 flex flex-col items-center justify-center"
                >
                  <Zap className="h-6 w-6 mb-2" />
                  اسکن RF
                </Button>
                
                <Button 
                  onClick={() => startScan('acoustic')}
                  disabled={scanStatus === 'scanning'}
                  className="h-20 flex flex-col items-center justify-center"
                >
                  <Activity className="h-6 w-6 mb-2" />
                  اسکن صوتی
                </Button>
                
                <Button 
                  onClick={() => startScan('thermal')}
                  disabled={scanStatus === 'scanning'}
                  className="h-20 flex flex-col items-center justify-center"
                >
                  <Target className="h-6 w-6 mb-2" />
                  اسکن حرارتی
                </Button>
                
                <Button 
                  onClick={() => startScan('power')}
                  disabled={scanStatus === 'scanning'}
                  className="h-20 flex flex-col items-center justify-center"
                >
                  <HardDrive className="h-6 w-6 mb-2" />
                  اسکن مصرف برق
                </Button>
                
                <Button 
                  onClick={() => startScan('comprehensive')}
                  disabled={scanStatus === 'scanning'}
                  className="h-20 flex flex-col items-center justify-center"
                >
                  <Search className="h-6 w-6 mb-2" />
                  اسکن جامع
                </Button>
              </div>
              
              {scanStatus === 'scanning' && (
                <div className="mt-4 flex items-center justify-center">
                  <Button onClick={stopScan} variant="destructive">
                    توقف اسکن
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>تنظیمات سیستم</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button variant="outline" className="h-12">
                  <Settings className="h-4 w-4 mr-2" />
                  تنظیمات عمومی
                </Button>
                <Button variant="outline" className="h-12">
                  <Shield className="h-4 w-4 mr-2" />
                  تنظیمات امنیت
                </Button>
                <Button variant="outline" className="h-12">
                  <Database className="h-4 w-4 mr-2" />
                  مدیریت پایگاه داده
                </Button>
                <Button variant="outline" className="h-12">
                  <Cpu className="h-4 w-4 mr-2" />
                  بهینه‌سازی سیستم
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}; 