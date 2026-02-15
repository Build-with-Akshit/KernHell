import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { MapPin, Users, Droplets, AlertTriangle, Info } from 'lucide-react';

export function VillageMap() {
  const [selectedVillage, setSelectedVillage] = useState<number | null>(null);

  const villages = [
    {
      id: 1,
      name: 'Jorhat',
      x: 65,
      y: 25,
      population: 2500,
      cases: 15,
      waterStatus: 'contaminated',
      riskLevel: 'high',
      healthWorkers: 3,
      waterSources: 2
    },
    {
      id: 2,
      name: 'Dibrugarh',
      x: 80,
      y: 30,
      population: 3200,
      cases: 23,
      waterStatus: 'safe',
      riskLevel: 'critical',
      healthWorkers: 4,
      waterSources: 3
    },
    {
      id: 3,
      name: 'Tezpur',
      x: 45,
      y: 40,
      population: 1800,
      cases: 8,
      waterStatus: 'warning',
      riskLevel: 'medium',
      healthWorkers: 2,
      waterSources: 2
    },
    {
      id: 4,
      name: 'Silchar',
      x: 50,
      y: 70,
      population: 2200,
      cases: 12,
      waterStatus: 'safe',
      riskLevel: 'medium',
      healthWorkers: 3,
      waterSources: 1
    },
    {
      id: 5,
      name: 'Nagaon',
      x: 35,
      y: 45,
      population: 1500,
      cases: 6,
      waterStatus: 'contaminated',
      riskLevel: 'high',
      healthWorkers: 2,
      waterSources: 1
    },
    {
      id: 6,
      name: 'Barpeta',
      x: 25,
      y: 35,
      population: 2800,
      cases: 18,
      waterStatus: 'warning',
      riskLevel: 'high',
      healthWorkers: 3,
      waterSources: 2
    }
  ];

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return '#10B981';
      case 'medium': return '#F59E0B';
      case 'high': return '#EF4444';
      case 'critical': return '#DC2626';
      default: return '#6B7280';
    }
  };

  const getWaterStatusColor = (status: string) => {
    switch (status) {
      case 'safe': return '#10B981';
      case 'warning': return '#F59E0B';
      case 'contaminated': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const selectedVillageData = selectedVillage ? villages.find(v => v.id === selectedVillage) : null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Visualization */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MapPin className="h-5 w-5 text-emerald-600" />
              <span>Northeast India - Village Coverage Map</span>
            </CardTitle>
            <CardDescription>Click on villages to view detailed information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative bg-gradient-to-br from-green-100 to-blue-100 rounded-lg p-6 h-96">
              {/* Rivers/Water bodies - simplified representation */}
              <div className="absolute top-10 left-10 w-32 h-2 bg-blue-300 rounded transform rotate-45 opacity-60"></div>
              <div className="absolute bottom-20 right-15 w-28 h-2 bg-blue-300 rounded transform -rotate-12 opacity-60"></div>
              
              {/* Villages */}
              {villages.map((village) => (
                <div key={village.id}>
                  {/* Village marker */}
                  <button
                    className="absolute transform -translate-x-1/2 -translate-y-1/2 hover:scale-110 transition-transform"
                    style={{ left: `${village.x}%`, top: `${village.y}%` }}
                    onClick={() => setSelectedVillage(village.id)}
                  >
                    <div 
                      className="w-6 h-6 rounded-full border-2 border-white shadow-lg flex items-center justify-center"
                      style={{ backgroundColor: getRiskColor(village.riskLevel) }}
                    >
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  </button>
                  
                  {/* Village label */}
                  <div
                    className="absolute transform -translate-x-1/2 translate-y-2 text-xs font-medium text-gray-700 bg-white px-2 py-1 rounded shadow-sm"
                    style={{ left: `${village.x}%`, top: `${village.y}%` }}
                  >
                    {village.name}
                  </div>
                  
                  {/* Risk indicator */}
                  {village.riskLevel === 'critical' && (
                    <div
                      className="absolute transform -translate-x-1/2 -translate-y-1/2 animate-ping"
                      style={{ left: `${village.x}%`, top: `${village.y}%` }}
                    >
                      <div className="w-8 h-8 bg-red-400 rounded-full opacity-75"></div>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Legend */}
              <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg">
                <h4 className="font-medium text-sm mb-2">Risk Levels</h4>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-xs">Low</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                    <span className="text-xs">Medium</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span className="text-xs">High</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-red-700"></div>
                    <span className="text-xs">Critical</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Village Details Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Info className="h-5 w-5" />
              <span>Village Details</span>
            </CardTitle>
            <CardDescription>
              {selectedVillageData ? `Information for ${selectedVillageData.name}` : 'Click on a village to view details'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selectedVillageData ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium">{selectedVillageData.name}</h3>
                  <Badge 
                    className={
                      selectedVillageData.riskLevel === 'critical' ? 'bg-red-100 text-red-800' :
                      selectedVillageData.riskLevel === 'high' ? 'bg-red-100 text-red-800' :
                      selectedVillageData.riskLevel === 'medium' ? 'bg-amber-100 text-amber-800' :
                      'bg-green-100 text-green-800'
                    }
                  >
                    {selectedVillageData.riskLevel.toUpperCase()} RISK
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <Users className="h-6 w-6 text-blue-600 mx-auto mb-1" />
                    <p className="text-sm text-muted-foreground">Population</p>
                    <p className="font-medium">{selectedVillageData.population.toLocaleString()}</p>
                  </div>
                  <div className="text-center p-3 bg-red-50 rounded-lg">
                    <AlertTriangle className="h-6 w-6 text-red-600 mx-auto mb-1" />
                    <p className="text-sm text-muted-foreground">Active Cases</p>
                    <p className="font-medium">{selectedVillageData.cases}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Water Status</span>
                    <Badge 
                      className={
                        selectedVillageData.waterStatus === 'safe' ? 'bg-green-100 text-green-800' :
                        selectedVillageData.waterStatus === 'warning' ? 'bg-amber-100 text-amber-800' :
                        'bg-red-100 text-red-800'
                      }
                    >
                      {selectedVillageData.waterStatus.toUpperCase()}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Health Workers</span>
                    <span className="font-medium">{selectedVillageData.healthWorkers}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Water Sources</span>
                    <span className="font-medium">{selectedVillageData.waterSources}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Infection Rate</span>
                    <span className="font-medium">
                      {((selectedVillageData.cases / selectedVillageData.population) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <Button 
                    size="sm" 
                    className="w-full bg-emerald-600 hover:bg-emerald-700"
                    onClick={() => {/* Could open detailed view */}}
                  >
                    View Full Report
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <MapPin className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>Select a village on the map to view detailed information</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Village Summary Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Villages Overview</CardTitle>
          <CardDescription>Complete status summary for all monitored villages</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-medium">Village</th>
                  <th className="text-left p-3 font-medium">Population</th>
                  <th className="text-left p-3 font-medium">Cases</th>
                  <th className="text-left p-3 font-medium">Water Status</th>
                  <th className="text-left p-3 font-medium">Risk Level</th>
                  <th className="text-left p-3 font-medium">Health Workers</th>
                </tr>
              </thead>
              <tbody>
                {villages.map((village) => (
                  <tr key={village.id} className="border-b hover:bg-muted/50 cursor-pointer" onClick={() => setSelectedVillage(village.id)}>
                    <td className="p-3 font-medium">{village.name}</td>
                    <td className="p-3">{village.population.toLocaleString()}</td>
                    <td className="p-3 font-medium">{village.cases}</td>
                    <td className="p-3">
                      <Badge 
                        size="sm"
                        className={
                          village.waterStatus === 'safe' ? 'bg-green-100 text-green-800' :
                          village.waterStatus === 'warning' ? 'bg-amber-100 text-amber-800' :
                          'bg-red-100 text-red-800'
                        }
                      >
                        {village.waterStatus}
                      </Badge>
                    </td>
                    <td className="p-3">
                      <Badge 
                        size="sm"
                        className={
                          village.riskLevel === 'critical' ? 'bg-red-100 text-red-800' :
                          village.riskLevel === 'high' ? 'bg-red-100 text-red-800' :
                          village.riskLevel === 'medium' ? 'bg-amber-100 text-amber-800' :
                          'bg-green-100 text-green-800'
                        }
                      >
                        {village.riskLevel}
                      </Badge>
                    </td>
                    <td className="p-3">{village.healthWorkers}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}