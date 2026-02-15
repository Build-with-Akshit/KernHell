import React, { useState } from 'react';
import { Alert, AlertDescription } from './ui/alert';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { X, AlertTriangle, Bell } from 'lucide-react';

export function AlertSystem() {
  const [alerts, setAlerts] = useState([
    {
      id: 1,
      type: 'critical',
      message: 'Water contamination detected in Jorhat Village - Immediate action required',
      timestamp: new Date(),
      dismissed: false
    },
    {
      id: 2,
      type: 'warning',
      message: 'Cholera cases rising in Dibrugarh area - Monitor closely',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      dismissed: false
    }
  ]);

  const dismissAlert = (id: number) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, dismissed: true } : alert
    ));
  };

  const activeAlerts = alerts.filter(alert => !alert.dismissed);

  if (activeAlerts.length === 0) return null;

  return (
    <div className="space-y-3 mb-6">
      {activeAlerts.map((alert) => (
        <Alert 
          key={alert.id} 
          className={`border-l-4 ${
            alert.type === 'critical' 
              ? 'border-l-red-500 bg-red-50' 
              : 'border-l-amber-500 bg-amber-50'
          }`}
        >
          <div className="flex items-start justify-between w-full">
            <div className="flex items-start space-x-3">
              {alert.type === 'critical' ? (
                <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              ) : (
                <Bell className="h-5 w-5 text-amber-600 mt-0.5" />
              )}
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <Badge 
                    className={
                      alert.type === 'critical' 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-amber-100 text-amber-800'
                    }
                  >
                    {alert.type.toUpperCase()}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {alert.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <AlertDescription className="text-sm">
                  {alert.message}
                </AlertDescription>
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => dismissAlert(alert.id)}
              className="h-6 w-6 p-0 hover:bg-transparent"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </Alert>
      ))}
    </div>
  );
}