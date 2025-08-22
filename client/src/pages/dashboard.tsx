import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import StatsOverview from '../components/StatsOverview';
import DeviceList from '../components/DeviceList';
import InteractiveMap from '../components/InteractiveMap';
import ScanControls from '../components/ScanControls';
import RecentActivity from '../components/RecentActivity';

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Ilam Province Mining Detection System</h1>
        <Button variant="outline" onClick={() => navigate('/auth')}>
          Logout
        </Button>
      </div>

      <StatsOverview />

      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-6">
          <ScanControls />
          <DeviceList />
        </div>
        <div className="space-y-6">
          <InteractiveMap />
          <RecentActivity />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
