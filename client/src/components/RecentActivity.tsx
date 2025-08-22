import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import useWebSocket from '../hooks/useWebSocket';
import { formatHashRate, formatPower } from '../lib/utils';

interface Activity {
  id: string;
  device_id: string;
  scan_time: string;
  scan_type: string;
  hash_rate?: number;
  power_consumption?: number;
  device: {
    ip_address: string;
    hostname?: string;
    location?: {
      city: string;
      province: string;
    };
  };
}

const RecentActivity = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const { isConnected } = useWebSocket('ws://localhost:8000/ws/activity', {
    onMessage: (message) => {
      if (message.type === 'activity') {
        setActivities(prev => [message.data, ...prev].slice(0, 10));
      }
    },
  });

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const response = await fetch('/api/activity?hours=1');
        const data = await response.json();
        setActivities(data);
      } catch (error) {
        console.error('Error fetching activities:', error);
      }
    };

    fetchActivities();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map(activity => (
            <div
              key={activity.id}
              className="flex items-center justify-between p-4 rounded-lg bg-muted/50"
            >
              <div>
                <div className="font-medium">
                  {activity.device.hostname || activity.device.ip_address}
                </div>
                <div className="text-sm text-muted-foreground">
                  {activity.device.location?.city}, {activity.device.location?.province}
                </div>
                <div className="text-sm text-muted-foreground">
                  {new Date(activity.scan_time).toLocaleString()}
                </div>
              </div>
              <div className="text-right">
                {activity.hash_rate && (
                  <div className="font-medium">{formatHashRate(activity.hash_rate)}</div>
                )}
                {activity.power_consumption && (
                  <div className="text-sm text-muted-foreground">
                    {formatPower(activity.power_consumption)}
                  </div>
                )}
                <div className="text-sm text-muted-foreground">
                  {activity.scan_type}
                </div>
              </div>
            </div>
          ))}
          {activities.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              No recent activity
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default RecentActivity;
