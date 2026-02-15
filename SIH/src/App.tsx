import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Dashboard } from './components/Dashboard';
import { WaterQualityMonitor } from './components/WaterQualityMonitor';
import { InfectionTrends } from './components/InfectionTrends';
import { VillageMap } from './components/VillageMap';
import { HealthWorkerForm } from './components/HealthWorkerForm';
import { CommunityEducation } from './components/CommunityEducation';
import { AlertSystem } from './components/AlertSystem';
import { Navigation } from './components/Navigation';
import { Tabs, TabsList, TabsTrigger } from './components/ui/tabs';

function AppContent() {
  const location = useLocation();
  const currentPath = location.pathname.substring(1) || 'dashboard';

  // Helper to map paths to tab values
  const getTabValue = (path: string) => {
    if (path === '' || path === '/') return 'dashboard';
    return path;
    };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-amber-50">
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        <Navigation />
        
        <div className="mt-6">
          <Tabs value={getTabValue(currentPath)} className="w-full">
            <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6 bg-emerald-100/50 mb-6">
              <TabsTrigger value="dashboard" asChild>
                <a href="/dashboard" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white block w-full h-full content-center">
                  Dashboard
                </a>
              </TabsTrigger>
              <TabsTrigger value="trends" asChild>
                <a href="/trends" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white block w-full h-full content-center">
                  Trends
                </a>
              </TabsTrigger>
              <TabsTrigger value="water" asChild>
                <a href="/water" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white block w-full h-full content-center">
                   Water Quality
                </a>
              </TabsTrigger>
              <TabsTrigger value="map" asChild>
                <a href="/map" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white block w-full h-full content-center">
                  Village Map
                </a>
              </TabsTrigger>
              <TabsTrigger value="input" asChild>
                <a href="/input" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white block w-full h-full content-center">
                  Data Entry
                </a>
              </TabsTrigger>
              <TabsTrigger value="education" asChild>
                 <a href="/education" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white block w-full h-full content-center">
                  Education
                </a>
              </TabsTrigger>
            </TabsList>

            <AlertSystem />

            <div className="space-y-6">
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/trends" element={<InfectionTrends />} />
                <Route path="/water" element={<WaterQualityMonitor />} />
                <Route path="/map" element={<VillageMap />} />
                <Route path="/input" element={<HealthWorkerForm />} />
                <Route path="/education" element={<CommunityEducation />} />
              </Routes>
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}
