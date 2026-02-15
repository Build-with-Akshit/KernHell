import React from 'react';
import { Activity, Droplets, MapPin } from 'lucide-react';
import { Card } from './ui/card';

export function Navigation() {
  return (
    <Card className="bg-emerald-800 text-white shadow-lg">
      <div className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-emerald-600 p-3 rounded-full">
              <Activity className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl lg:text-2xl font-medium">Community Health Monitor</h1>
              <p className="text-emerald-200 text-sm">Northeast India Water-borne Disease Prevention</p>
            </div>
          </div>
          
          <div className="hidden lg:flex items-center space-x-6 text-emerald-200">
            <div className="flex items-center space-x-2">
              <Droplets className="h-4 w-4" />
              <span className="text-sm">Water Quality Tracking</span>
            </div>
            <div className="flex items-center space-x-2">
              <MapPin className="h-4 w-4" />
              <span className="text-sm">Village Coverage</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}