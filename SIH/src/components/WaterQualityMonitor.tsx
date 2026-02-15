import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Droplets, Zap, Thermometer, Beaker, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

export function WaterQualityMonitor() {
  const waterSources = [
    {
      id: 1,
      name: 'Jorhat Main Well',
      village: 'Jorhat',
      status: 'contaminated',
      ph: 6.2,
      bacteria: 850,
      chlorine: 0.3,
      temperature: 24,
      lastTested: '2 hours ago',
      issues: ['High bacteria count', 'Low pH']
    },
    {
      id: 2,
      name: 'Dibrugarh Bore Well',
      village: 'Dibrugarh',
      status: 'safe',
      ph: 7.1,
      bacteria: 12,
      chlorine: 0.8,
      temperature: 22,
      lastTested: '4 hours ago',
      issues: []
    },
    {
      id: 3,
      name: 'Tezpur Community Tank',
      village: 'Tezpur',
      status: 'warning',
      ph: 8.2,
      bacteria: 45,
      chlorine: 1.2,
      temperature: 26,
      lastTested: '6 hours ago',
      issues: ['High pH', 'Elevated temperature']
    },
    {
      id: 4,
      name: 'Silchar Hand Pump',
      village: 'Silchar',
      status: 'safe',
      ph: 7.0,
      bacteria: 8,
      chlorine: 0.9,
      temperature: 23,
      lastTested: '1 day ago',
      issues: []
    },
    {
      id: 5,
      name: 'Nagaon River Intake',
      village: 'Nagaon',
      status: 'contaminated',
      ph: 5.8,
      bacteria: 1200,
      chlorine: 0.1,
      temperature: 28,
      lastTested: '3 hours ago',
      issues: ['Very high bacteria', 'Low chlorine', 'Acidic pH']
    },
    {
      id: 6,
      name: 'Barpeta Deep Well',
      village: 'Barpeta',
      status: 'warning',
      ph: 7.8,
      bacteria: 35,
      chlorine: 0.6,
      temperature: 25,
      lastTested: '5 hours ago',
      issues: ['Slightly high pH']
    }
  ];

  const qualityMetrics = [
    {
      title: 'Safe Water Sources',
      count: waterSources.filter(s => s.status === 'safe').length,
      total: waterSources.length,
      percentage: Math.round((waterSources.filter(s => s.status === 'safe').length / waterSources.length) * 100),
      icon: CheckCircle,
      color: 'text-green-600'
    },
    {
      title: 'Sources Needing Attention',
      count: waterSources.filter(s => s.status === 'warning').length,
      total: waterSources.length,
      percentage: Math.round((waterSources.filter(s => s.status === 'warning').length / waterSources.length) * 100),
      icon: AlertCircle,
      color: 'text-amber-600'
    },
    {
      title: 'Contaminated Sources',
      count: waterSources.filter(s => s.status === 'contaminated').length,
      total: waterSources.length,
      percentage: Math.round((waterSources.filter(s => s.status === 'contaminated').length / waterSources.length) * 100),
      icon: XCircle,
      color: 'text-red-600'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe': return 'bg-green-100 text-green-800';
      case 'warning': return 'bg-amber-100 text-amber-800';
      case 'contaminated': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'safe': return CheckCircle;
      case 'warning': return AlertCircle;
      case 'contaminated': return XCircle;
      default: return AlertCircle;
    }
  };

  const getPHColor = (ph: number) => {
    if (ph >= 6.5 && ph <= 8.5) return 'text-green-600';
    return 'text-red-600';
  };

  const getBacteriaColor = (bacteria: number) => {
    if (bacteria < 100) return 'text-green-600';
    if (bacteria < 500) return 'text-amber-600';
    return 'text-red-600';
  };

  const getChlorineColor = (chlorine: number) => {
    if (chlorine >= 0.5 && chlorine <= 1.0) return 'text-green-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Quality Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {qualityMetrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{metric.title}</p>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className="text-2xl font-medium">{metric.count}</span>
                      <span className="text-lg text-muted-foreground">/ {metric.total}</span>
                    </div>
                    <div className="mt-3">
                      <Progress value={metric.percentage} className="h-2" />
                      <p className="text-xs text-muted-foreground mt-1">{metric.percentage}%</p>
                    </div>
                  </div>
                  <Icon className={`h-8 w-8 ${metric.color}`} />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Critical Alerts */}
      <div className="space-y-3">
        {waterSources.filter(source => source.status === 'contaminated').map((source) => (
          <Alert key={source.id} className="border-l-4 border-l-red-500 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription>
              <strong>{source.name}</strong> in {source.village} is contaminated. 
              Issues: {source.issues.join(', ')}. Immediate action required.
            </AlertDescription>
          </Alert>
        ))}
      </div>

      {/* Water Sources Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {waterSources.map((source) => {
          const StatusIcon = getStatusIcon(source.status);
          return (
            <Card key={source.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{source.name}</CardTitle>
                    <CardDescription>{source.village} Village</CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={getStatusColor(source.status)}>
                      {source.status.charAt(0).toUpperCase() + source.status.slice(1)}
                    </Badge>
                    <StatusIcon className={`h-5 w-5 ${source.status === 'safe' ? 'text-green-600' : source.status === 'warning' ? 'text-amber-600' : 'text-red-600'}`} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <Beaker className="h-4 w-4 text-blue-600" />
                    <div>
                      <p className="text-xs text-muted-foreground">pH Level</p>
                      <p className={`font-medium ${getPHColor(source.ph)}`}>{source.ph}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Zap className="h-4 w-4 text-purple-600" />
                    <div>
                      <p className="text-xs text-muted-foreground">Bacteria (CFU/ml)</p>
                      <p className={`font-medium ${getBacteriaColor(source.bacteria)}`}>{source.bacteria}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Droplets className="h-4 w-4 text-cyan-600" />
                    <div>
                      <p className="text-xs text-muted-foreground">Chlorine (mg/L)</p>
                      <p className={`font-medium ${getChlorineColor(source.chlorine)}`}>{source.chlorine}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Thermometer className="h-4 w-4 text-orange-600" />
                    <div>
                      <p className="text-xs text-muted-foreground">Temperature (°C)</p>
                      <p className="font-medium">{source.temperature}</p>
                    </div>
                  </div>
                </div>
                
                {source.issues.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs text-muted-foreground">Issues Detected:</p>
                    <div className="flex flex-wrap gap-1">
                      {source.issues.map((issue, index) => (
                        <Badge key={index} variant="destructive" className="text-xs">
                          {issue}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-between items-center mt-4 pt-4 border-t">
                  <p className="text-xs text-muted-foreground">
                    Last tested: {source.lastTested}
                  </p>
                  <Badge variant="outline" className="text-xs">
                    {source.status === 'contaminated' ? 'Urgent' : 'Regular'} Monitoring
                  </Badge>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Water Quality Guidelines */}
      <Card>
        <CardHeader>
          <CardTitle>Water Quality Guidelines</CardTitle>
          <CardDescription>WHO recommended standards for drinking water</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Beaker className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h4 className="font-medium mb-1">pH Level</h4>
              <p className="text-sm text-muted-foreground">6.5 - 8.5</p>
              <p className="text-xs text-blue-600 mt-1">Optimal Range</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Zap className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h4 className="font-medium mb-1">Bacteria</h4>
              <p className="text-sm text-muted-foreground">&lt; 100 CFU/ml</p>
              <p className="text-xs text-purple-600 mt-1">Safe Limit</p>
            </div>
            <div className="text-center p-4 bg-cyan-50 rounded-lg">
              <Droplets className="h-8 w-8 text-cyan-600 mx-auto mb-2" />
              <h4 className="font-medium mb-1">Chlorine</h4>
              <p className="text-sm text-muted-foreground">0.5 - 1.0 mg/L</p>
              <p className="text-xs text-cyan-600 mt-1">Disinfection Level</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <Thermometer className="h-8 w-8 text-orange-600 mx-auto mb-2" />
              <h4 className="font-medium mb-1">Temperature</h4>
              <p className="text-sm text-muted-foreground">15 - 25°C</p>
              <p className="text-xs text-orange-600 mt-1">Ideal Range</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}