import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from './ui/card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface Stats {
  total_devices: number;
  confirmed_miners: number;
  suspicious_devices: number;
  scans_24h: number;
  timestamp: string;
}

const StatsOverview = () => {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/overview');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    // Fetch stats every minute
    fetchStats();
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, []);

  if (!stats) {
    return <div>Loading...</div>;
  }

  const chartData = [
    {
      name: 'Confirmed',
      value: stats.confirmed_miners,
      fill: '#ef4444',
    },
    {
      name: 'Suspicious',
      value: stats.suspicious_devices,
      fill: '#eab308', 
    },
    {
      name: 'Other',
      value: stats.total_devices - stats.confirmed_miners - stats.suspicious_devices,
      fill: '#22c55e',
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Detection Overview</CardTitle>
          <CardDescription>Last updated: {new Date(stats.timestamp).toLocaleString()}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold">{stats.total_devices}</div>
              <div className="text-sm text-muted-foreground">Total Devices</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-destructive">{stats.confirmed_miners}</div>
              <div className="text-sm text-muted-foreground">Confirmed Miners</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-500">{stats.suspicious_devices}</div>
              <div className="text-sm text-muted-foreground">Suspicious Devices</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-500">{stats.scans_24h}</div>
              <div className="text-sm text-muted-foreground">Scans (24h)</div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Device Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" name="Devices" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default StatsOverview;
