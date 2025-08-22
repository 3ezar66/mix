import React, { useEffect, useState } from 'react';
import {
  Table,
  TableBody, 
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { Card } from './ui/card';
import { Badge } from './ui/badge';

interface Device {
  id: string;
  ip_address: string;
  hostname: string;
  first_seen: string;
  last_seen: string; 
  confidence_score: number;
  detection_methods: string[];
  location: any;
  owner: any;
}

const DeviceList = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await fetch('/api/miners');
        const data = await response.json();
        setDevices(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching devices:', error);
        setLoading(false);
      }
    };

    // Fetch every 30 seconds
    fetchDevices();
    const interval = setInterval(fetchDevices, 30000);
    return () => clearInterval(interval);
  }, []);

  const getConfidenceColor = (score: number): "destructive" | "secondary" | "default" => {
    if (score >= 80) return "destructive";
    if (score >= 60) return "secondary"; 
    return "default";
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <Card>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>IP Address</TableHead>
            <TableHead>Hostname</TableHead>
            <TableHead>First Seen</TableHead>
            <TableHead>Last Seen</TableHead>
            <TableHead>Confidence</TableHead>
            <TableHead>Detection Methods</TableHead>
            <TableHead>Location</TableHead>
            <TableHead>Owner</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {devices.map((device) => (
            <TableRow key={device.id}>
              <TableCell>{device.ip_address}</TableCell>
              <TableCell>{device.hostname}</TableCell>
              <TableCell>{new Date(device.first_seen).toLocaleString()}</TableCell>
              <TableCell>{new Date(device.last_seen).toLocaleString()}</TableCell>
              <TableCell>
                <Badge variant={getConfidenceColor(device.confidence_score)}>
                  {device.confidence_score}%
                </Badge>
              </TableCell>
              <TableCell>
                {device.detection_methods.map((method) => (
                  <Badge key={method} variant="secondary" className="mr-1">
                    {method}
                  </Badge>
                ))}
              </TableCell>
              <TableCell>
                {device.location.city}, {device.location.province}
              </TableCell>
              <TableCell>
                {device.owner.name} ({device.owner.type})
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
};

export default DeviceList;
