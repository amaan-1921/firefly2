"use client";

import { useState, useMemo } from "react";
import { Filter, ArrowUpDown, Clock, AlertCircle, CheckCircle, XCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Activity {
  id: string;
  type: "alert" | "update" | "resolved" | "created";
  title: string;
  description: string;
  timestamp: Date;
  severity?: "critical" | "high" | "medium" | "low";
  user?: string;
  category?: string;
}

const mockActivities: Activity[] = [
  {
    id: "1",
    type: "alert",
    title: "New critical alert created",
    description: "Supply chain disruption detected in Asia-Pacific region",
    timestamp: new Date(Date.now() - 5 * 60000),
    severity: "critical",
    user: "System",
    category: "supply_chain",
  },
  {
    id: "2",
    type: "update",
    title: "Alert status updated",
    description: "Logistics delay alert marked as in progress",
    timestamp: new Date(Date.now() - 15 * 60000),
    severity: "high",
    user: "John Doe",
    category: "logistics",
  },
  {
    id: "3",
    type: "resolved",
    title: "Alert resolved",
    description: "Manufacturing quality issue has been resolved",
    timestamp: new Date(Date.now() - 30 * 60000),
    severity: "medium",
    user: "Jane Smith",
    category: "manufacturing",
  },
  {
    id: "4",
    type: "created",
    title: "New supplier onboarded",
    description: "Tech Components Ltd added to supplier network",
    timestamp: new Date(Date.now() - 60 * 60000),
    user: "Admin",
    category: "procurement",
  },
];

const getActivityIcon = (type: Activity["type"]) => {
  switch (type) {
    case "alert":
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    case "update":
      return <Clock className="h-4 w-4 text-blue-500" />;
    case "resolved":
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case "created":
      return <CheckCircle className="h-4 w-4 text-purple-500" />;
  }
};

const getSeverityColor = (severity?: string) => {
  switch (severity) {
    case "critical":
      return "destructive";
    case "high":
      return "destructive";
    case "medium":
      return "default";
    case "low":
      return "secondary";
    default:
      return "outline";
  }
};

const formatTimestamp = (date: Date) => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
};

export function RecentActivity() {
  const [activities] = useState<Activity[]>(mockActivities);
  const [filterType, setFilterType] = useState<string>("all");
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"date" | "severity">("date");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const filteredAndSortedActivities = useMemo(() => {
    let filtered = activities;

    // Filter by type
    if (filterType !== "all") {
      filtered = filtered.filter((a) => a.type === filterType);
    }

    // Filter by severity
    if (filterSeverity !== "all") {
      filtered = filtered.filter((a) => a.severity === filterSeverity);
    }

    // Sort
    return filtered.sort((a, b) => {
      if (sortBy === "date") {
        const comparison = a.timestamp.getTime() - b.timestamp.getTime();
        return sortOrder === "asc" ? comparison : -comparison;
      } else {
        // Sort by severity
        const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        const aVal = severityOrder[a.severity as keyof typeof severityOrder] || 0;
        const bVal = severityOrder[b.severity as keyof typeof severityOrder] || 0;
        const comparison = aVal - bVal;
        return sortOrder === "asc" ? comparison : -comparison;
      }
    });
  }, [activities, filterType, filterSeverity, sortBy, sortOrder]);

  const toggleSortOrder = () => {
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              {filteredAndSortedActivities.length} activities
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={toggleSortOrder}>
              <ArrowUpDown className="h-4 w-4 mr-1" />
              {sortOrder === "asc" ? "Oldest" : "Latest"}
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2 pt-4">
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-[140px]">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="alert">Alerts</SelectItem>
              <SelectItem value="update">Updates</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
              <SelectItem value="created">Created</SelectItem>
            </SelectContent>
          </Select>

          <Select value={filterSeverity} onValueChange={setFilterSeverity}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Severity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Severities</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>

          <Select value={sortBy} onValueChange={(v) => setSortBy(v as "date" | "severity")}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="date">Date</SelectItem>
              <SelectItem value="severity">Severity</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          {filteredAndSortedActivities.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[200px] text-muted-foreground">
              <XCircle className="h-12 w-12 mb-2 opacity-20" />
              <p>No activities found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAndSortedActivities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex gap-4 p-3 rounded-lg border hover:bg-accent transition-colors"
                >
                  <div className="mt-1">{getActivityIcon(activity.type)}</div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-sm">{activity.title}</p>
                        <p className="text-sm text-muted-foreground">
                          {activity.description}
                        </p>
                      </div>
                      {activity.severity && (
                        <Badge
                          variant={getSeverityColor(activity.severity) as any}
                          className="ml-2"
                        >
                          {activity.severity}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>{formatTimestamp(activity.timestamp)}</span>
                      {activity.user && (
                        <>
                          <span>•</span>
                          <span>{activity.user}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}