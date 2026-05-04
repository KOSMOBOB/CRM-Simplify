'use client';

import { useAuth } from '@/lib/auth-context';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

// Mock data - in production, fetch from API
const metricsData = [
  { name: 'Total Contacts', value: 1247, change: '+12%', trend: 'up' },
  { name: 'Active Leads', value: 89, change: '+5%', trend: 'up' },
  { name: 'Deals Won', value: 34, change: '+18%', trend: 'up' },
  { name: 'Revenue (MTD)', value: '$124,500', change: '+22%', trend: 'up' },
];

const activityData = [
  { date: 'Mon', activities: 12, deals: 3 },
  { date: 'Tue', activities: 18, deals: 5 },
  { date: 'Wed', activities: 15, deals: 4 },
  { date: 'Thu', activities: 22, deals: 7 },
  { date: 'Fri', activities: 19, deals: 6 },
  { date: 'Sat', activities: 8, deals: 2 },
  { date: 'Sun', activities: 5, deals: 1 },
];

const pipelineData = [
  { stage: 'New', count: 25, value: 125000 },
  { stage: 'Contacted', count: 18, value: 95000 },
  { stage: 'Qualified', count: 12, value: 78000 },
  { stage: 'Proposal', count: 8, value: 52000 },
  { stage: 'Won', count: 15, value: 185000 },
];

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Badge variant="info">Welcome, {user?.email || 'User'}</Badge>
      </div>

      {/* Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metricsData.map((metric) => (
          <Card key={metric.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{metric.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <p className={`text-xs ${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {metric.change} from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Activity Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={activityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="activities" fill="#3b82f6" name="Activities" />
                <Bar dataKey="deals" fill="#22c55e" name="Deals Closed" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Pipeline Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={pipelineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#8884d8" strokeWidth={2} name="Deals Count" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { type: 'Call', contact: 'John Doe', time: '10 min ago', status: 'completed' },
              { type: 'Email', contact: 'Jane Smith', time: '1 hour ago', status: 'sent' },
              { type: 'Meeting', contact: 'Acme Corp', time: '2 hours ago', status: 'scheduled' },
              { type: 'Task', contact: 'Follow up with Bob', time: '3 hours ago', status: 'pending' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between border-b pb-3 last:border-0">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-medium">{activity.type[0]}</span>
                  </div>
                  <div>
                    <p className="font-medium">{activity.contact}</p>
                    <p className="text-sm text-muted-foreground">{activity.type}</p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant={
                    activity.status === 'completed' ? 'success' :
                    activity.status === 'sent' ? 'info' :
                    activity.status === 'scheduled' ? 'warning' : 'secondary'
                  }>
                    {activity.status}
                  </Badge>
                  <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
