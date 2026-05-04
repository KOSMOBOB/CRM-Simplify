'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { DndContext, DragEndEvent } from '@dnd-kit/core';

interface Deal {
  id: string;
  title: string;
  company: string;
  value: number;
  stage: 'new' | 'contacted' | 'qualified' | 'proposal' | 'won' | 'lost';
  probability: number;
  owner: string;
}

const STAGES = [
  { id: 'new', title: 'New', color: 'info' },
  { id: 'contacted', title: 'Contacted', color: 'warning' },
  { id: 'qualified', title: 'Qualified', color: 'default' },
  { id: 'proposal', title: 'Proposal', color: 'default' },
  { id: 'won', title: 'Won', color: 'success' },
  { id: 'lost', title: 'Lost', color: 'destructive' },
] as const;

export default function PipelinePage() {
  const queryClient = useQueryClient();
  const [draggedDealId, setDraggedDealId] = useState<string | null>(null);

  // Fetch deals - with mock fallback if API is not available
  const { data: deals = [], isLoading } = useQuery({
    queryKey: ['deals'],
    queryFn: async () => {
      try {
        const response = await api.get('/api/v1/deals');
        return response.data;
      } catch (error) {
        // Mock data for demo purposes
        console.log('Using mock data - API not available');
        return [
          { id: '1', title: 'Enterprise License', company: 'TechCorp', value: 150000, stage: 'new', probability: 20, owner: 'John' },
          { id: '2', title: 'Startup Package', company: 'StartupIO', value: 35000, stage: 'contacted', probability: 40, owner: 'Sarah' },
          { id: '3', title: 'Annual Contract', company: 'Enterprise Co', value: 250000, stage: 'qualified', probability: 60, owner: 'Mike' },
          { id: '4', title: 'Consulting Deal', company: 'GrowthCo', value: 85000, stage: 'proposal', probability: 75, owner: 'John' },
          { id: '5', title: 'Partnership', company: 'SolutionsNet', value: 120000, stage: 'won', probability: 100, owner: 'Sarah' },
          { id: '6', title: 'Small Biz Deal', company: 'LocalShop', value: 15000, stage: 'lost', probability: 0, owner: 'Mike' },
          { id: '7', title: 'Cloud Migration', company: 'DataFlow', value: 95000, stage: 'new', probability: 25, owner: 'Sarah' },
          { id: '8', title: 'Security Audit', company: 'SecureInc', value: 45000, stage: 'qualified', probability: 65, owner: 'John' },
        ] as Deal[];
      }
    },
  });

  const updateStageMutation = useMutation({
    mutationFn: async ({ id, stage }: { id: string; stage: string }) => {
      return api.patch(`/api/v1/deals/${id}/stage`, { stage });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deals'] });
    },
  });

  const handleDragEnd = (event: DragEndEvent) => {
    const { over } = event;
    if (over && draggedDealId) {
      const newStage = over.id as Deal['stage'];
      updateStageMutation.mutate({ id: draggedDealId, stage: newStage });
    }
    setDraggedDealId(null);
  };

  const getDealsByStage = (stage: string) => deals.filter((deal: Deal) => deal.stage === stage);

  const getTotalValue = (stage: string) => {
    return getDealsByStage(stage).reduce((sum: number, deal: Deal) => sum + deal.value, 0);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Sales Pipeline</h1>
        <Button>Add Deal</Button>
      </div>

      {isLoading ? (
        <p className="text-center text-muted-foreground py-8">Loading pipeline...</p>
      ) : (
        <DndContext onDragEnd={handleDragEnd}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {STAGES.map((stage) => (
              <Card key={stage.id} className="flex flex-col">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-semibold">{stage.title}</CardTitle>
                    <Badge variant={stage.color as any} className="text-xs">
                      {getDealsByStage(stage.id).length}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    ${getTotalValue(stage.id).toLocaleString()}
                  </p>
                </CardHeader>
                <CardContent className="flex-1 space-y-2 overflow-auto min-h-[400px]">
                  {getDealsByStage(stage.id).map((deal) => (
                    <div
                      key={deal.id}
                      draggable
                      onDragStart={() => setDraggedDealId(deal.id)}
                      onDragEnd={() => setDraggedDealId(null)}
                      className="p-3 rounded-lg border bg-card hover:shadow-md cursor-move transition-shadow"
                    >
                      <div className="font-medium text-sm mb-1">{deal.title}</div>
                      <div className="text-xs text-muted-foreground mb-2">{deal.company}</div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold">${deal.value.toLocaleString()}</span>
                        <span className="text-xs text-muted-foreground">{deal.probability}%</span>
                      </div>
                      <div className="mt-2 flex items-center justify-between text-xs">
                        <Badge variant="outline">{deal.owner}</Badge>
                      </div>
                    </div>
                  ))}
                  {getDealsByStage(stage.id).length === 0 && (
                    <div className="text-center text-muted-foreground py-8 text-sm">
                      No deals in this stage
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </DndContext>
      )}

      {/* Pipeline Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Total Deals</p>
              <p className="text-2xl font-bold">{deals.length}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Pipeline Value</p>
              <p className="text-2xl font-bold">
                ${deals.filter((d: Deal) => !['won', 'lost'].includes(d.stage)).reduce((sum: number, d: Deal) => sum + d.value, 0).toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Win Rate</p>
              <p className="text-2xl font-bold">
                {deals.length > 0 ? Math.round((deals.filter((d: Deal) => d.stage === 'won').length / deals.length) * 100) : 0}%
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Avg Deal Size</p>
              <p className="text-2xl font-bold">
                ${deals.length > 0 ? Math.round(deals.reduce((sum: number, d: Deal) => sum + d.value, 0) / deals.length).toLocaleString() : 0}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
