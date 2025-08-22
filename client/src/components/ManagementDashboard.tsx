import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Activity, 
  Map, 
  Users, 
  Shield, 
  Zap, 
  Wifi, 
  Radio, 
  Thermometer,
  Volume2,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  BarChart3,
  Settings,
  Database,
  Network,
  Satellite,
  Building2,
  Car,
  FileText,
  Download,
  Upload,
  Eye,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Calendar,
  TrendingUp,
  TrendingDown,
  PieChart,
  LineChart,
  Globe,
  Phone,
  Mail,
  User,
  Key,
  Lock,
  Unlock,
  RefreshCw,
  Play,
  Pause,
  Square,
  RotateCcw
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

interface SystemOverview {
  totalDetections: number;
  activeMiners: number;
  confirmedMiners: number;
  suspiciousDevices: number;
  totalPowerConsumption: number;
  networkHealth: number;
  rfSignalsDetected: number;
  acousticSignatures: number;
  thermalAnomalies: number;
  recentAlerts: number;
  systemStatus: 'operational' | 'warning' | 'critical';
  uptime: string;
  lastScan: string;
  activeScans: number;
}

interface DetectionDetail {
  id: string;
  ipAddress: string;
  macAddress: string;
  location: {
    latitude: number;
    longitude: number;
    address: string;
    city: string;
    region: string;
  };
  owner: {
    name: string;
    phone: string;
    nationalId: string;
    address: string;
    verificationStatus: string;
  };
  detectionMethods: string[];
  confidenceScore: number;
  threatLevel: 'low' | 'medium' | 'high' | 'critical';
  deviceType: string;
  powerConsumption: number;
  hashRate: string;
  timestamp: string;
  status: 'active' | 'inactive' | 'investigating' | 'resolved';
  notes: string;
}

interface ScanSession {
  id: string;
  sessionType: string;
  ipRange: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  startTime: string;
  endTime?: string;
  devicesFound: number;
  minersDetected: number;
  priority: 'low' | 'normal' | 'high' | 'critical';
  progress: number;
}

interface User {
  id: number;
  username: string;
  role: 'admin' | 'operator' | 'viewer';
  lastLogin: string;
  status: 'active' | 'inactive';
  permissions: string[];
}

const ManagementDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedDetection, setSelectedDetection] = useState<DetectionDetail | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterThreatLevel, setFilterThreatLevel] = useState('all');
  const queryClient = useQueryClient();

  // Fetch system overview
  const { data: overview, isLoading: overviewLoading } = useQuery<SystemOverview>({
    queryKey: ['system-overview'],
    queryFn: async () => {
      const response = await axios.get('/api/v2/status');
      return response.data;
    },
    refetchInterval: 30000
  });

  // Fetch detections
  const { data: detections, isLoading: detectionsLoading } = useQuery<DetectionDetail[]>({
    queryKey: ['detections', searchTerm, filterStatus, filterThreatLevel],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (filterStatus !== 'all') params.append('status', filterStatus);
      if (filterThreatLevel !== 'all') params.append('threat_level', filterThreatLevel);
      
      const response = await axios.get(`/api/v2/detections?${params.toString()}`);
      return response.data;
    }
  });

  // Fetch scan sessions
  const { data: scanSessions, isLoading: scanSessionsLoading } = useQuery<ScanSession[]>({
    queryKey: ['scan-sessions'],
    queryFn: async () => {
      const response = await axios.get('/api/v2/scans');
      return response.data;
    },
    refetchInterval: 10000
  });

  // Fetch users
  const { data: users, isLoading: usersLoading } = useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await axios.get('/api/v2/users');
      return response.data;
    }
  });

  // Mutations
  const startScanMutation = useMutation({
    mutationFn: async (scanConfig: any) => {
      const response = await axios.post('/api/v2/scan/comprehensive', scanConfig);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scan-sessions'] });
      queryClient.invalidateQueries({ queryKey: ['system-overview'] });
    }
  });

  const updateDetectionMutation = useMutation({
    mutationFn: async ({ id, updates }: { id: string; updates: any }) => {
      const response = await axios.patch(`/api/v2/detections/${id}`, updates);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['detections'] });
    }
  });

  const updateUserMutation = useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: any }) => {
      const response = await axios.put(`/api/v2/users/${id}`, updates);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    }
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-orange-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getScanStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-600';
      case 'completed': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'paused': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const getDetectionMethodIcon = (method: string) => {
    switch (method) {
      case 'network_analysis': return <Network className="w-4 h-4" />;
      case 'acoustic_signature': return <Volume2 className="w-4 h-4" />;
      case 'thermal_signature': return <Thermometer className="w-4 h-4" />;
      case 'rf_analysis': return <Radio className="w-4 h-4" />;
      case 'power_consumption': return <Zap className="w-4 h-4" />;
      default: return <Target className="w-4 h-4" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">داشبورد مدیریتی سیستم جامع ملی</h1>
          <p className="text-gray-600 mt-2">مدیریت کامل سیستم کشف ماینرهای غیرمجاز</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant={overview?.systemStatus === 'operational' ? 'default' : 'destructive'}>
            {overview?.systemStatus === 'operational' ? 'عملیاتی' : 'هشدار'}
          </Badge>
          <Button onClick={() => window.location.reload()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            بروزرسانی
          </Button>
        </div>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="overview">نمای کلی</TabsTrigger>
          <TabsTrigger value="detections">تشخیص‌ها</TabsTrigger>
          <TabsTrigger value="scans">اسکن‌ها</TabsTrigger>
          <TabsTrigger value="users">کاربران</TabsTrigger>
          <TabsTrigger value="reports">گزارشات</TabsTrigger>
          <TabsTrigger value="analytics">تحلیل‌ها</TabsTrigger>
          <TabsTrigger value="settings">تنظیمات</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* System Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">کل تشخیص‌ها</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overview?.totalDetections || 0}</div>
                <p className="text-xs text-muted-foreground">
                  +{overview?.recentAlerts || 0} در 24 ساعت گذشته
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">ماینرهای فعال</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overview?.activeMiners || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {overview?.confirmedMiners || 0} تأیید شده
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">مصرف برق کل</CardTitle>
                <Zap className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {overview?.totalPowerConsumption ? `${(overview.totalPowerConsumption / 1000).toFixed(1)} کیلووات` : '0 کیلووات'}
                </div>
                <p className="text-xs text-muted-foreground">
                  معادل {overview?.totalPowerConsumption ? Math.round(overview.totalPowerConsumption / 1000) : 0} خانه
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">وضعیت شبکه</CardTitle>
                <Wifi className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{overview?.networkHealth || 0}%</div>
                <Progress value={overview?.networkHealth || 0} className="mt-2" />
              </CardContent>
            </Card>
          </div>

          {/* System Health Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>وضعیت سیستم</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Database className="w-4 h-4" />
                    <span>پایگاه داده</span>
                  </div>
                  <Badge variant="default">سالم</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Network className="w-4 h-4" />
                    <span>شبکه</span>
                  </div>
                  <Badge variant="default">سالم</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Radio className="w-4 h-4" />
                    <span>تشخیص RF</span>
                  </div>
                  <Badge variant="default">سالم</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Volume2 className="w-4 h-4" />
                    <span>تشخیص صوتی</span>
                  </div>
                  <Badge variant="default">سالم</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Thermometer className="w-4 h-4" />
                    <span>تشخیص حرارتی</span>
                  </div>
                  <Badge variant="default">سالم</Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>آمار کلی</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span>زمان کارکرد:</span>
                  <span className="font-medium">{overview?.uptime || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span>آخرین اسکن:</span>
                  <span className="font-medium">{overview?.lastScan || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span>اسکن‌های فعال:</span>
                  <span className="font-medium">{overview?.activeScans || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>سیگنال‌های RF:</span>
                  <span className="font-medium">{overview?.rfSignalsDetected || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>امضاهای صوتی:</span>
                  <span className="font-medium">{overview?.acousticSignatures || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>ناهنجاری‌های حرارتی:</span>
                  <span className="font-medium">{overview?.thermalAnomalies || 0}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Detections Tab */}
        <TabsContent value="detections" className="space-y-6">
          {/* Filters and Search */}
          <Card>
            <CardHeader>
              <CardTitle>فیلتر و جستجو</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <Label htmlFor="search">جستجو</Label>
                  <Input
                    id="search"
                    placeholder="جستجو بر اساس IP، آدرس یا نام مالک..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="status">وضعیت</Label>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">همه</SelectItem>
                      <SelectItem value="active">فعال</SelectItem>
                      <SelectItem value="inactive">غیرفعال</SelectItem>
                      <SelectItem value="investigating">در حال بررسی</SelectItem>
                      <SelectItem value="resolved">حل شده</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="threat">سطح تهدید</Label>
                  <Select value={filterThreatLevel} onValueChange={setFilterThreatLevel}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">همه</SelectItem>
                      <SelectItem value="low">کم</SelectItem>
                      <SelectItem value="medium">متوسط</SelectItem>
                      <SelectItem value="high">زیاد</SelectItem>
                      <SelectItem value="critical">بحرانی</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-end">
                  <Button className="w-full">
                    <Filter className="w-4 h-4 mr-2" />
                    اعمال فیلتر
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detections List */}
          <Card>
            <CardHeader>
              <CardTitle>لیست تشخیص‌ها</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {detections?.map((detection) => (
                  <div 
                    key={detection.id} 
                    className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedDetection(detection)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div>
                          <h3 className="font-medium">{detection.ipAddress}</h3>
                          <p className="text-sm text-gray-500">{detection.location.address}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          {detection.detectionMethods.map((method) => (
                            <div key={method} className="flex items-center space-x-1">
                              {getDetectionMethodIcon(method)}
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <p className="text-sm font-medium">{detection.owner.name}</p>
                          <p className="text-xs text-gray-500">{detection.owner.phone}</p>
                        </div>
                        <Badge className={getThreatLevelColor(detection.threatLevel)}>
                          {detection.threatLevel}
                        </Badge>
                        <div className="text-right">
                          <p className="text-sm font-medium">{detection.confidenceScore}%</p>
                          <p className="text-xs text-gray-500">اطمینان</p>
                        </div>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="outline">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Scans Tab */}
        <TabsContent value="scans" className="space-y-6">
          {/* Scan Controls */}
          <Card>
            <CardHeader>
              <CardTitle>کنترل اسکن‌ها</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button 
                  onClick={() => startScanMutation.mutate({ 
                    ipRange: '192.168.1.0/24',
                    ports: [22, 80, 443, 4028, 8080, 9999],
                    timeout: 3,
                    detection_methods: ["network", "rf", "acoustic", "thermal", "power"],
                    priority: "normal"
                  })}
                  disabled={startScanMutation.isPending}
                >
                  {startScanMutation.isPending ? 'در حال شروع...' : 'شروع اسکن جدید'}
                </Button>
                <Button variant="outline">
                  <Pause className="w-4 h-4 mr-2" />
                  توقف همه اسکن‌ها
                </Button>
                <Button variant="outline">
                  <RotateCcw className="w-4 h-4 mr-2" />
                  بازنشانی
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Active Scans */}
          <Card>
            <CardHeader>
              <CardTitle>اسکن‌های فعال</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {scanSessions?.filter(s => s.status === 'running').map((scan) => (
                  <div key={scan.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h3 className="font-medium">{scan.sessionType} - {scan.ipRange}</h3>
                        <p className="text-sm text-gray-500">شروع: {scan.startTime}</p>
                      </div>
                      <Badge className={getScanStatusColor(scan.status)}>
                        {scan.status}
                      </Badge>
                    </div>
                    <Progress value={scan.progress} className="mb-2" />
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>پیشرفت: {scan.progress}%</span>
                      <span>دستگاه‌های یافت شده: {scan.devicesFound}</span>
                      <span>ماینرهای تشخیص داده شده: {scan.minersDetected}</span>
                    </div>
                    <div className="flex space-x-2 mt-2">
                      <Button size="sm" variant="outline">
                        <Pause className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Square className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Scans */}
          <Card>
            <CardHeader>
              <CardTitle>اسکن‌های اخیر</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {scanSessions?.filter(s => s.status !== 'running').slice(0, 10).map((scan) => (
                  <div key={scan.id} className="flex items-center justify-between p-2 border rounded">
                    <div>
                      <p className="font-medium">{scan.sessionType}</p>
                      <p className="text-sm text-gray-500">{scan.ipRange}</p>
                    </div>
                    <div className="text-right">
                      <Badge className={getScanStatusColor(scan.status)}>
                        {scan.status}
                      </Badge>
                      <p className="text-sm text-gray-500">{scan.minersDetected} ماینر</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6">
          {/* User Management */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>مدیریت کاربران</CardTitle>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  افزودن کاربر جدید
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users?.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-4 border rounded">
                    <div className="flex items-center space-x-4">
                      <div>
                        <p className="font-medium">{user.username}</p>
                        <p className="text-sm text-gray-500">{user.role}</p>
                      </div>
                      <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                        {user.status}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-2">
                      <p className="text-sm text-gray-500">آخرین ورود: {user.lastLogin}</p>
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Key className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline" className="text-red-600">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>گزارشات</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button variant="outline" className="h-20 flex-col">
                  <FileText className="w-6 h-6 mb-2" />
                  گزارش روزانه
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <BarChart3 className="w-6 h-6 mb-2" />
                  گزارش هفتگی
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <TrendingUp className="w-6 h-6 mb-2" />
                  گزارش ماهانه
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <Globe className="w-6 h-6 mb-2" />
                  گزارش جغرافیایی
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <Zap className="w-6 h-6 mb-2" />
                  گزارش مصرف انرژی
                </Button>
                <Button variant="outline" className="h-20 flex-col">
                  <Download className="w-6 h-6 mb-2" />
                  خروجی Excel
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>تحلیل روند</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">نمودار روند در حال بارگذاری...</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>توزیع جغرافیایی</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">نقشه توزیع در حال بارگذاری...</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>تنظیمات سیستم</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>حساسیت تشخیص</span>
                  <Settings className="w-4 h-4" />
                </div>
                <div className="flex items-center justify-between">
                  <span>فاصله زمانی اسکن</span>
                  <Clock className="w-4 h-4" />
                </div>
                <div className="flex items-center justify-between">
                  <span>تنظیمات هشدار</span>
                  <AlertTriangle className="w-4 h-4" />
                </div>
                <div className="flex items-center justify-between">
                  <span>تنظیمات امنیتی</span>
                  <Lock className="w-4 h-4" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Detection Detail Modal */}
      {selectedDetection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">جزئیات تشخیص</h2>
              <Button variant="outline" onClick={() => setSelectedDetection(null)}>
                بستن
              </Button>
            </div>
            
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <Label>آدرس IP</Label>
                  <p className="font-medium">{selectedDetection.ipAddress}</p>
                </div>
                <div>
                  <Label>MAC Address</Label>
                  <p className="font-medium">{selectedDetection.macAddress || 'نامشخص'}</p>
                </div>
                <div>
                  <Label>نوع دستگاه</Label>
                  <p className="font-medium">{selectedDetection.deviceType}</p>
                </div>
                <div>
                  <Label>مصرف برق</Label>
                  <p className="font-medium">{selectedDetection.powerConsumption} وات</p>
                </div>
                <div>
                  <Label>نرخ هش</Label>
                  <p className="font-medium">{selectedDetection.hashRate || 'نامشخص'}</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label>نام مالک</Label>
                  <p className="font-medium">{selectedDetection.owner.name}</p>
                </div>
                <div>
                  <Label>تلفن</Label>
                  <p className="font-medium">{selectedDetection.owner.phone}</p>
                </div>
                <div>
                  <Label>کد ملی</Label>
                  <p className="font-medium">{selectedDetection.owner.nationalId}</p>
                </div>
                <div>
                  <Label>آدرس</Label>
                  <p className="font-medium">{selectedDetection.owner.address}</p>
                </div>
                <div>
                  <Label>وضعیت تأیید</Label>
                  <Badge variant={selectedDetection.owner.verificationStatus === 'verified' ? 'default' : 'secondary'}>
                    {selectedDetection.owner.verificationStatus}
                  </Badge>
                </div>
              </div>
            </div>
            
            <div className="mt-6">
              <Label>یادداشت‌ها</Label>
              <p className="mt-2">{selectedDetection.notes || 'یادداشتی وجود ندارد'}</p>
            </div>
            
            <div className="flex space-x-2 mt-6">
              <Button onClick={() => updateDetectionMutation.mutate({ 
                id: selectedDetection.id, 
                updates: { status: 'investigating' } 
              })}>
                شروع بررسی
              </Button>
              <Button variant="outline">
                مشاهده نقشه
              </Button>
              <Button variant="outline">
                دانلود گزارش
              </Button>
              <Button variant="outline">
                ویرایش
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManagementDashboard;