import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Slider } from './ui/slider';
import { Switch } from './ui/switch';
import { Alert, AlertDescription } from './ui/alert';
import { SearchCheck } from 'lucide-react';

interface ScanOptions {
  ipRange: string;
  portRange: string;
  intensity: number;
  useRF: boolean;
  useAI: boolean;
}

const ScanControls = () => {
  const [scanning, setScanning] = useState(false);
  const [options, setOptions] = useState<ScanOptions>({
    ipRange: '192.168.1.1-254',
    portRange: '1-65535',
    intensity: 50,
    useRF: true,
    useAI: true,
  });
  const [status, setStatus] = useState<string | null>(null);

  const startScan = async () => {
    try {
      setScanning(true);
      setStatus('شروع اسکن...');

      const response = await fetch('/api/scan/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(options),
      });

      if (!response.ok) throw new Error('خطا در شروع اسکن');

      setStatus('اسکن در حال انجام...');
    } catch (error) {
      console.error('Error starting scan:', error);
      setStatus('خطا در شروع اسکن');
      setScanning(false);
    }
  };

  const stopScan = async () => {
    try {
      const response = await fetch('/api/scan/stop', {
        method: 'POST',
      });

      if (!response.ok) throw new Error('خطا در متوقف کردن اسکن');

      setScanning(false);
      setStatus('اسکن متوقف شد');
    } catch (error) {
      console.error('Error stopping scan:', error);
      setStatus('خطا در متوقف کردن اسکن');
    }
  };

  return (
    <Card className="persian-card mb-6">
      <CardHeader>
        <CardTitle className="flex items-center text-lg">
          <SearchCheck className="ml-2 h-5 w-5 text-primary" />
          کنترل‌های اسکن و شناسایی
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4">
          <div className="space-y-2">
            <Label htmlFor="ipRange">محدوده IP</Label>
            <Input
              id="ipRange"
              placeholder="192.168.1.1-254"
              value={options.ipRange}
              onChange={(e) => setOptions({ ...options, ipRange: e.target.value })}
              disabled={scanning}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="portRange">محدوده پورت</Label>
            <Input
              id="portRange"
              placeholder="1-65535"
              value={options.portRange}
              onChange={(e) => setOptions({ ...options, portRange: e.target.value })}
              disabled={scanning}
            />
          </div>
          <div className="space-y-2">
            <Label>شدت اسکن</Label>
            <Slider
              value={[options.intensity]}
              onValueChange={(values) => setOptions({ ...options, intensity: values[0] })}
              max={100}
              step={1}
              disabled={scanning}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="rf"
              checked={options.useRF}
              onCheckedChange={(checked) => setOptions({ ...options, useRF: checked })}
              disabled={scanning}
            />
            <Label htmlFor="rf">فعال‌سازی تشخیص RF</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="ai"
              checked={options.useAI}
              onCheckedChange={(checked) => setOptions({ ...options, useAI: checked })}
              disabled={scanning}
            />
            <Label htmlFor="ai">فعال‌سازی تحلیل AI</Label>
          </div>
        </div>

        <div className="flex space-x-2">
          {!scanning ? (
            <Button onClick={startScan} className="bg-primary hover:bg-blue-600 focus-ring">
              شروع اسکن
            </Button>
          ) : (
            <Button onClick={stopScan} variant="destructive">
              متوقف کردن اسکن
            </Button>
          )}
        </div>

        {status && (
          <Alert>
            <AlertDescription>{status}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ScanControls;
