import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { UserPlus, Save, CheckCircle, Droplets, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner@2.0.3';

export function HealthWorkerForm() {
  const [formData, setFormData] = useState({
    workerName: '',
    village: '',
    reportDate: new Date().toISOString().split('T')[0],
    symptoms: [] as string[],
    caseCount: '',
    ageGroup: '',
    waterSource: '',
    waterQuality: '',
    notes: '',
    urgency: 'low'
  });

  const [recentSubmissions, setRecentSubmissions] = useState([
    {
      id: 1,
      worker: 'Dr. Anita Sharma',
      village: 'Jorhat',
      date: '2024-01-10',
      cases: 5,
      status: 'processed'
    },
    {
      id: 2,
      worker: 'Nurse Ravi Kumar',
      village: 'Dibrugarh',
      date: '2024-01-09',
      cases: 3,
      status: 'pending'
    },
    {
      id: 3,
      worker: 'ASHA Meera Devi',
      village: 'Tezpur',
      date: '2024-01-08',
      cases: 2,
      status: 'processed'
    }
  ]);

  const villages = [
    'Jorhat', 'Dibrugarh', 'Tezpur', 'Silchar', 'Nagaon', 'Barpeta',
    'Golaghat', 'Lakhimpur', 'Dhubri', 'Karimganj'
  ];

  const symptoms = [
    'Diarrhea', 'Vomiting', 'Fever', 'Abdominal pain', 
    'Dehydration', 'Nausea', 'Headache', 'Fatigue'
  ];

  const waterSources = [
    'Hand pump', 'Tube well', 'Open well', 'Community tank',
    'River/stream', 'Pond', 'Spring', 'Piped water'
  ];

  const handleSymptomChange = (symptom: string, checked: boolean) => {
    if (checked) {
      setFormData(prev => ({
        ...prev,
        symptoms: [...prev.symptoms, symptom]
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        symptoms: prev.symptoms.filter(s => s !== symptom)
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.workerName || !formData.village || !formData.caseCount) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Simulate submission
    const newSubmission = {
      id: Date.now(),
      worker: formData.workerName,
      village: formData.village,
      date: formData.reportDate,
      cases: parseInt(formData.caseCount),
      status: 'pending' as const
    };

    setRecentSubmissions(prev => [newSubmission, ...prev.slice(0, 4)]);
    
    // Reset form
    setFormData({
      workerName: '',
      village: '',
      reportDate: new Date().toISOString().split('T')[0],
      symptoms: [],
      caseCount: '',
      ageGroup: '',
      waterSource: '',
      waterQuality: '',
      notes: '',
      urgency: 'low'
    });

    toast.success('Health report submitted successfully!');
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <UserPlus className="h-5 w-5 text-emerald-600" />
              <span>Health Worker Data Entry</span>
            </CardTitle>
            <CardDescription>
              Submit new health data and water quality observations from the field
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Worker and Location Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="workerName">Health Worker Name *</Label>
                  <Input
                    id="workerName"
                    value={formData.workerName}
                    onChange={(e) => setFormData(prev => ({ ...prev, workerName: e.target.value }))}
                    placeholder="Enter your full name"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="village">Village *</Label>
                  <Select 
                    value={formData.village} 
                    onValueChange={(value) => setFormData(prev => ({ ...prev, village: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select village" />
                    </SelectTrigger>
                    <SelectContent>
                      {villages.map((village) => (
                        <SelectItem key={village} value={village}>{village}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="reportDate">Report Date</Label>
                  <Input
                    id="reportDate"
                    type="date"
                    value={formData.reportDate}
                    onChange={(e) => setFormData(prev => ({ ...prev, reportDate: e.target.value }))}
                  />
                </div>
                <div>
                  <Label htmlFor="caseCount">Number of Cases *</Label>
                  <Input
                    id="caseCount"
                    type="number"
                    min="0"
                    value={formData.caseCount}
                    onChange={(e) => setFormData(prev => ({ ...prev, caseCount: e.target.value }))}
                    placeholder="0"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="ageGroup">Primary Age Group</Label>
                  <Select 
                    value={formData.ageGroup} 
                    onValueChange={(value) => setFormData(prev => ({ ...prev, ageGroup: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select age group" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0-5">0-5 years</SelectItem>
                      <SelectItem value="6-18">6-18 years</SelectItem>
                      <SelectItem value="19-60">19-60 years</SelectItem>
                      <SelectItem value="60+">60+ years</SelectItem>
                      <SelectItem value="mixed">Mixed ages</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Symptoms */}
              <div>
                <Label>Observed Symptoms</Label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2">
                  {symptoms.map((symptom) => (
                    <div key={symptom} className="flex items-center space-x-2">
                      <Checkbox
                        id={symptom}
                        checked={formData.symptoms.includes(symptom)}
                        onCheckedChange={(checked) => handleSymptomChange(symptom, !!checked)}
                      />
                      <Label htmlFor={symptom} className="text-sm">{symptom}</Label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Water Quality */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>Primary Water Source</Label>
                  <Select 
                    value={formData.waterSource} 
                    onValueChange={(value) => setFormData(prev => ({ ...prev, waterSource: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select water source" />
                    </SelectTrigger>
                    <SelectContent>
                      {waterSources.map((source) => (
                        <SelectItem key={source} value={source}>{source}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Water Quality Assessment</Label>
                  <Select 
                    value={formData.waterQuality} 
                    onValueChange={(value) => setFormData(prev => ({ ...prev, waterQuality: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Assess water quality" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="clean">Clean/Safe</SelectItem>
                      <SelectItem value="cloudy">Cloudy/Turbid</SelectItem>
                      <SelectItem value="odor">Strange odor</SelectItem>
                      <SelectItem value="contaminated">Visibly contaminated</SelectItem>
                      <SelectItem value="unknown">Cannot assess</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Urgency and Notes */}
              <div>
                <Label>Urgency Level</Label>
                <Select 
                  value={formData.urgency} 
                  onValueChange={(value) => setFormData(prev => ({ ...prev, urgency: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low - Routine monitoring</SelectItem>
                    <SelectItem value="medium">Medium - Increased attention needed</SelectItem>
                    <SelectItem value="high">High - Urgent intervention required</SelectItem>
                    <SelectItem value="critical">Critical - Immediate action needed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="notes">Additional Notes</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                  placeholder="Any additional observations, community concerns, or recommendations..."
                  rows={4}
                />
              </div>

              {/* Submit Button */}
              <div className="flex justify-end">
                <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700">
                  <Save className="h-4 w-4 mr-2" />
                  Submit Report
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Recent Submissions & Quick Actions */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Droplets className="h-4 w-4 mr-2" />
                Report Water Contamination
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <AlertTriangle className="h-4 w-4 mr-2" />
                Emergency Health Alert
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <CheckCircle className="h-4 w-4 mr-2" />
                Mark Area as Safe
              </Button>
            </CardContent>
          </Card>

          {/* Recent Submissions */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Submissions</CardTitle>
              <CardDescription>Latest reports from health workers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentSubmissions.map((submission) => (
                  <div key={submission.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium text-sm">{submission.worker}</p>
                      <p className="text-xs text-muted-foreground">{submission.village}</p>
                      <p className="text-xs text-muted-foreground">{submission.date}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-sm">{submission.cases} cases</p>
                      <Badge 
                        size="sm"
                        className={
                          submission.status === 'processed' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-amber-100 text-amber-800'
                        }
                      >
                        {submission.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle>Reporting Guidelines</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>• Report all suspected water-borne disease cases</p>
              <p>• Include water source assessment when possible</p>
              <p>• Use high/critical urgency for outbreaks</p>
              <p>• Document community concerns in notes</p>
              <p>• Contact supervisor for emergency cases</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Info Alert */}
      <Alert className="border-emerald-200 bg-emerald-50">
        <CheckCircle className="h-4 w-4 text-emerald-600" />
        <AlertDescription className="text-emerald-800">
          All submitted data is immediately processed and shared with the district health office. 
          Emergency reports trigger automatic notifications to supervisors.
        </AlertDescription>
      </Alert>
    </div>
  );
}