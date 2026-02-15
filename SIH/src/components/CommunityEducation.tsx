import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Separator } from './ui/separator';
import { BookOpen, Play, Download, Users, CheckCircle, AlertTriangle, Droplets, Shield } from 'lucide-react';

export function CommunityEducation() {
  const [completedModules, setCompletedModules] = useState<number[]>([1, 3]);

  const educationalModules = [
    {
      id: 1,
      title: 'Water-borne Diseases: Understanding the Risks',
      description: 'Learn about common water-borne diseases in Northeast India and their symptoms',
      duration: '15 minutes',
      language: 'English, Assamese, Bengali',
      type: 'video',
      difficulty: 'Beginner',
      topics: ['Cholera', 'Diarrhea', 'Typhoid', 'Prevention']
    },
    {
      id: 2,
      title: 'Safe Water Practices for Rural Communities',
      description: 'Essential water treatment and storage methods for rural households',
      duration: '20 minutes',
      language: 'English, Assamese',
      type: 'interactive',
      difficulty: 'Beginner',
      topics: ['Water treatment', 'Storage', 'Testing', 'Household tips']
    },
    {
      id: 3,
      title: 'Recognizing Early Warning Signs',
      description: 'How to identify symptoms and when to seek medical help',
      duration: '12 minutes',
      language: 'Multiple languages',
      type: 'video',
      difficulty: 'Beginner',
      topics: ['Symptoms', 'Emergency signs', 'First aid', 'Medical help']
    },
    {
      id: 4,
      title: 'Community Health Monitoring',
      description: 'Training for village health volunteers and community leaders',
      duration: '45 minutes',
      language: 'English, Assamese',
      type: 'course',
      difficulty: 'Intermediate',
      topics: ['Data collection', 'Reporting', 'Community engagement', 'Leadership']
    }
  ];

  const resources = [
    {
      title: 'Water Safety Poster (Assamese)',
      type: 'poster',
      size: '2.1 MB',
      format: 'PDF',
      description: 'Visual guide for safe water practices'
    },
    {
      title: 'Disease Prevention Handbook',
      type: 'handbook',
      size: '5.8 MB',
      format: 'PDF',
      description: 'Comprehensive prevention guide for families'
    },
    {
      title: 'Emergency Contact Numbers',
      type: 'reference',
      size: '156 KB',
      format: 'PDF',
      description: 'Important health department contacts'
    },
    {
      title: 'Water Testing Kit Instructions',
      type: 'manual',
      size: '3.2 MB',
      format: 'PDF',
      description: 'How to use basic water testing kits'
    }
  ];

  const communityPrograms = [
    {
      title: 'Village Health Champion Training',
      date: 'January 15-17, 2024',
      location: 'Jorhat District Office',
      participants: '25 community leaders',
      status: 'upcoming',
      focus: 'Training local leaders to monitor and report health issues'
    },
    {
      title: 'Women\'s Health Awareness Workshop',
      date: 'January 20, 2024',
      location: 'Multiple villages',
      participants: '150+ women',
      status: 'upcoming',
      focus: 'Maternal and child health during disease outbreaks'
    },
    {
      title: 'School Water Safety Program',
      date: 'December 2023',
      location: '12 local schools',
      participants: '800+ students',
      status: 'completed',
      focus: 'Teaching children about water safety and hygiene'
    }
  ];

  const handleModuleComplete = (moduleId: number) => {
    if (!completedModules.includes(moduleId)) {
      setCompletedModules(prev => [...prev, moduleId]);
    }
  };

  return (
    <div className="space-y-6">
      <Tabs defaultValue="modules" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-emerald-100/50">
          <TabsTrigger value="modules" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            Learning Modules
          </TabsTrigger>
          <TabsTrigger value="resources" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            Resources
          </TabsTrigger>
          <TabsTrigger value="programs" className="data-[state=active]:bg-emerald-600 data-[state=active]:text-white">
            Community Programs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="modules" className="space-y-6">
          {/* Progress Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-emerald-600" />
                <span>Learning Progress</span>
              </CardTitle>
              <CardDescription>Track your community education progress</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-emerald-50 rounded-lg">
                  <div className="text-2xl font-medium text-emerald-600">{completedModules.length}</div>
                  <p className="text-sm text-emerald-700">Modules Completed</p>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-medium text-blue-600">{educationalModules.length - completedModules.length}</div>
                  <p className="text-sm text-blue-700">Modules Remaining</p>
                </div>
                <div className="text-center p-4 bg-amber-50 rounded-lg">
                  <div className="text-2xl font-medium text-amber-600">
                    {Math.round((completedModules.length / educationalModules.length) * 100)}%
                  </div>
                  <p className="text-sm text-amber-700">Progress</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Learning Modules */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {educationalModules.map((module) => (
              <Card key={module.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{module.title}</CardTitle>
                      <CardDescription className="mt-2">{module.description}</CardDescription>
                    </div>
                    {completedModules.includes(module.id) && (
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-2">
                      {module.topics.map((topic) => (
                        <Badge key={topic} variant="secondary" className="text-xs">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                      <div>
                        <span className="font-medium">Duration:</span> {module.duration}
                      </div>
                      <div>
                        <span className="font-medium">Type:</span> {module.type}
                      </div>
                      <div>
                        <span className="font-medium">Level:</span> {module.difficulty}
                      </div>
                      <div>
                        <span className="font-medium">Languages:</span> {module.language}
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <Button 
                        size="sm" 
                        className="bg-emerald-600 hover:bg-emerald-700"
                        onClick={() => handleModuleComplete(module.id)}
                        disabled={completedModules.includes(module.id)}
                      >
                        <Play className="h-4 w-4 mr-2" />
                        {completedModules.includes(module.id) ? 'Completed' : 'Start Module'}
                      </Button>
                      <Button size="sm" variant="outline">
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="resources" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Download className="h-5 w-5 text-emerald-600" />
                <span>Educational Resources</span>
              </CardTitle>
              <CardDescription>Download materials for community education and awareness</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {resources.map((resource, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-blue-100 rounded">
                        <Download className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-medium">{resource.title}</h4>
                        <p className="text-sm text-muted-foreground">{resource.description}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {resource.format} • {resource.size}
                        </p>
                      </div>
                    </div>
                    <Button size="sm" variant="outline">
                      Download
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Reference Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-blue-50 to-blue-100">
              <CardContent className="p-6 text-center">
                <Droplets className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                <h3 className="font-medium mb-2">Water Safety</h3>
                <p className="text-sm text-muted-foreground">Boil water for 1 minute before drinking</p>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-green-50 to-green-100">
              <CardContent className="p-6 text-center">
                <Shield className="h-8 w-8 text-green-600 mx-auto mb-3" />
                <h3 className="font-medium mb-2">Prevention</h3>
                <p className="text-sm text-muted-foreground">Wash hands frequently with soap</p>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-amber-50 to-amber-100">
              <CardContent className="p-6 text-center">
                <AlertTriangle className="h-8 w-8 text-amber-600 mx-auto mb-3" />
                <h3 className="font-medium mb-2">Warning Signs</h3>
                <p className="text-sm text-muted-foreground">Severe diarrhea + dehydration = Emergency</p>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-br from-purple-50 to-purple-100">
              <CardContent className="p-6 text-center">
                <Users className="h-8 w-8 text-purple-600 mx-auto mb-3" />
                <h3 className="font-medium mb-2">Community</h3>
                <p className="text-sm text-muted-foreground">Report cases to health workers</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="programs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-emerald-600" />
                <span>Community Programs</span>
              </CardTitle>
              <CardDescription>Health education and awareness programs in local communities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {communityPrograms.map((program, index) => (
                  <div key={index} className="border rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-medium text-lg">{program.title}</h3>
                        <p className="text-muted-foreground mt-1">{program.focus}</p>
                      </div>
                      <Badge 
                        className={
                          program.status === 'completed' ? 'bg-green-100 text-green-800' :
                          program.status === 'upcoming' ? 'bg-blue-100 text-blue-800' :
                          'bg-amber-100 text-amber-800'
                        }
                      >
                        {program.status.toUpperCase()}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Date:</span>
                        <p className="font-medium">{program.date}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Location:</span>
                        <p className="font-medium">{program.location}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Participants:</span>
                        <p className="font-medium">{program.participants}</p>
                      </div>
                    </div>
                    
                    {index < communityPrograms.length - 1 && <Separator className="mt-6" />}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Community Impact */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-medium text-emerald-600 mb-2">1,200+</div>
                <p className="text-muted-foreground">People Trained</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-medium text-blue-600 mb-2">45</div>
                <p className="text-muted-foreground">Villages Reached</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-3xl font-medium text-purple-600 mb-2">15</div>
                <p className="text-muted-foreground">Programs Completed</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}