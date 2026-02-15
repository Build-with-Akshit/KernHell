import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Calendar, BarChart3 } from 'lucide-react';

export function InfectionTrends() {
  const weeklyData = [
    { week: 'Week 1', cholera: 5, diarrhea: 12, typhoid: 2, total: 19 },
    { week: 'Week 2', cholera: 8, diarrhea: 15, typhoid: 3, total: 26 },
    { week: 'Week 3', cholera: 3, diarrhea: 8, typhoid: 1, total: 12 },
    { week: 'Week 4', cholera: 6, diarrhea: 11, typhoid: 4, total: 21 },
    { week: 'Week 5', cholera: 4, diarrhea: 7, typhoid: 2, total: 13 },
    { week: 'Week 6', cholera: 7, diarrhea: 14, typhoid: 3, total: 24 },
  ];

  const villageData = [
    { village: 'Jorhat', cases: 15, population: 2500 },
    { village: 'Dibrugarh', cases: 23, population: 3200 },
    { village: 'Tezpur', cases: 8, population: 1800 },
    { village: 'Silchar', cases: 12, population: 2200 },
    { village: 'Nagaon', cases: 6, population: 1500 },
    { village: 'Barpeta', cases: 18, population: 2800 },
  ];

  const diseaseDistribution = [
    { name: 'Diarrhea', value: 45, color: '#8B5CF6' },
    { name: 'Cholera', value: 30, color: '#EF4444' },
    { name: 'Typhoid', value: 15, color: '#F59E0B' },
    { name: 'Others', value: 10, color: '#10B981' },
  ];

  const trends = [
    {
      disease: 'Cholera',
      currentWeek: 7,
      lastWeek: 4,
      trend: 'up',
      change: '+75%'
    },
    {
      disease: 'Diarrhea',
      currentWeek: 14,
      lastWeek: 11,
      trend: 'up',
      change: '+27%'
    },
    {
      disease: 'Typhoid',
      currentWeek: 3,
      lastWeek: 4,
      trend: 'down',
      change: '-25%'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Trend Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {trends.map((trend, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">{trend.disease}</h3>
                  <div className="flex items-center space-x-2 mt-2">
                    <span className="text-2xl font-medium">{trend.currentWeek}</span>
                    <Badge 
                      className={
                        trend.trend === 'up' 
                          ? 'bg-red-100 text-red-800' 
                          : 'bg-green-100 text-green-800'
                      }
                    >
                      {trend.change}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">This week</p>
                </div>
                {trend.trend === 'up' ? (
                  <TrendingUp className="h-8 w-8 text-red-500" />
                ) : (
                  <TrendingDown className="h-8 w-8 text-green-500" />
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calendar className="h-5 w-5" />
              <span>Weekly Infection Trends</span>
            </CardTitle>
            <CardDescription>Disease cases over the past 6 weeks</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="cholera" stroke="#EF4444" strokeWidth={2} />
                <Line type="monotone" dataKey="diarrhea" stroke="#8B5CF6" strokeWidth={2} />
                <Line type="monotone" dataKey="typhoid" stroke="#F59E0B" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Disease Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Disease Distribution</span>
            </CardTitle>
            <CardDescription>Breakdown of all reported cases</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={diseaseDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {diseaseDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Village Comparison */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Cases by Village</CardTitle>
            <CardDescription>Infection rates across monitored villages</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={villageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="village" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'cases' ? `${value} cases` : `${value} people`,
                    name === 'cases' ? 'Total Cases' : 'Population'
                  ]}
                />
                <Legend />
                <Bar dataKey="cases" fill="#DC2626" name="cases" />
                <Bar dataKey="population" fill="#059669" name="population" opacity={0.6} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Key Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
          <CardDescription>Important trends and patterns from the data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                <h4 className="text-red-800 font-medium mb-2">⚠️ Alert: Cholera Spike</h4>
                <p className="text-red-700 text-sm">
                  Cholera cases have increased by 75% this week. Dibrugarh village showing highest concentration.
                </p>
              </div>
              <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                <h4 className="text-amber-800 font-medium mb-2">📊 Pattern: Seasonal Increase</h4>
                <p className="text-amber-700 text-sm">
                  Diarrheal diseases typically peak during monsoon season. Prepare preventive measures.
                </p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="text-green-800 font-medium mb-2">✅ Success: Typhoid Control</h4>
                <p className="text-green-700 text-sm">
                  Typhoid cases decreased by 25% following improved sanitation efforts in affected areas.
                </p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="text-blue-800 font-medium mb-2">💡 Recommendation</h4>
                <p className="text-blue-700 text-sm">
                  Focus water quality testing on Dibrugarh and Barpeta villages based on case concentrations.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}