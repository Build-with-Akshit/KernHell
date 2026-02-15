import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { AlertTriangle, Users, Droplets, Shield, TrendingUp, TrendingDown } from 'lucide-react';

export function Dashboard() {
  const keyMetrics = [
    {
      title: 'Active Cases',
      value: '23',
      change: '+3 from last week',
      trend: 'up',
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    },
    {
      title: 'Villages Monitored',
      value: '45',
      change: '+2 new villages',
      trend: 'up',
      icon: Users,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50'
    },
    {
      title: 'Water Sources Tested',
      value: '127',
      change: '98% safe this week',
      trend: 'up',
      icon: Droplets,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Prevention Rate',
      value: '94%',
      change: '+2% improvement',
      trend: 'up',
      icon: Shield,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    }
  ];

  const recentAlerts = [
    {
      village: 'Jorhat Village',
      issue: 'Water contamination detected',
      severity: 'high',
      time: '2 hours ago'
    },
    {
      village: 'Dibrugarh Settlement',
      issue: 'New cholera cases reported',
      severity: 'critical',
      time: '4 hours ago'
    },
    {
      village: 'Tezpur Community',
      issue: 'Water quality improved',
      severity: 'low',
      time: '1 day ago'
    }
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {keyMetrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-muted-foreground text-sm">{metric.title}</p>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className="text-2xl font-medium">{metric.value}</span>
                      {metric.trend === 'up' ? (
                        <TrendingUp className="h-4 w-4 text-green-600" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-600" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{metric.change}</p>
                  </div>
                  <div className={`${metric.bgColor} p-3 rounded-full`}>
                    <Icon className={`h-5 w-5 ${metric.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Alerts and Status Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              <span>Recent Alerts</span>
            </CardTitle>
            <CardDescription>Latest health and water quality alerts from monitored villages</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentAlerts.map((alert, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h4 className="font-medium">{alert.village}</h4>
                      <Badge className={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{alert.issue}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{alert.time}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Health Status Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Health Status Overview</CardTitle>
            <CardDescription>Current health metrics across all villages</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm">Water Safety</span>
                <span className="text-sm">94%</span>
              </div>
              <Progress value={94} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm">Vaccination Coverage</span>
                <span className="text-sm">87%</span>
              </div>
              <Progress value={87} className="h-2" />
            </div>
            
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm">Health Worker Coverage</span>
                <span className="text-sm">76%</span>
              </div>
              <Progress value={76} className="h-2" />
            </div>
            
            <div className="pt-4 border-t">
              <div className="text-center">
                <div className="text-2xl font-medium text-emerald-600">45</div>
                <div className="text-sm text-muted-foreground">Villages Protected</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}