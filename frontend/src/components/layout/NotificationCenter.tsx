"use client";

import { useState } from "react";
import { Bell, X, Check, AlertTriangle, Info, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface Notification {
  id: string;
  type: "info" | "warning" | "success" | "error";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  link?: string;
}

const mockNotifications: Notification[] = [
  {
    id: "1",
    type: "error",
    title: "Critical Alert",
    message: "Supply chain disruption detected in Asia-Pacific region",
    timestamp: new Date(Date.now() - 5 * 60000),
    read: false,
    link: "/dashboard/alerts",
  },
  {
    id: "2",
    type: "warning",
    title: "Supplier Risk",
    message: "High-risk supplier activity detected",
    timestamp: new Date(Date.now() - 30 * 60000),
    read: false,
    link: "/dashboard/suppliers",
  },
  {
    id: "3",
    type: "success",
    title: "Recommendation Applied",
    message: "Your diversification strategy has been successfully implemented",
    timestamp: new Date(Date.now() - 2 * 60 * 60000),
    read: true,
  },
  {
    id: "4",
    type: "info",
    title: "New Report Available",
    message: "Monthly supply chain health report is ready",
    timestamp: new Date(Date.now() - 24 * 60 * 60000),
    read: true,
    link: "/dashboard/monitoring",
  },
];

const getNotificationIcon = (type: Notification["type"]) => {
  switch (type) {
    case "error":
      return <AlertTriangle className="h-4 w-4 text-red-500" />;
    case "warning":
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    case "success":
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case "info":
    default:
      return <Info className="h-4 w-4 text-blue-500" />;
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

export function NotificationCenter() {
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);
  const [isOpen, setIsOpen] = useState(false);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const deleteNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unreadCount > 9 ? "9+" : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="end">
        <div className="flex items-center justify-between p-4 border-b">
          <div>
            <h3 className="font-semibold text-lg">Notifications</h3>
            <p className="text-sm text-muted-foreground">
              You have {unreadCount} unread {unreadCount === 1 ? "notification" : "notifications"}
            </p>
          </div>
          {unreadCount > 0 && (
            <Button variant="ghost" size="sm" onClick={markAllAsRead}>
              <Check className="h-4 w-4 mr-1" />
              Mark all read
            </Button>
          )}
        </div>

        <ScrollArea className="h-[400px]">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[200px] text-muted-foreground">
              <Bell className="h-12 w-12 mb-2 opacity-20" />
              <p>No notifications</p>
            </div>
          ) : (
            <div className="divide-y">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={cn(
                    "p-4 hover:bg-accent transition-colors group",
                    !notification.read && "bg-accent/50"
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-1">{getNotificationIcon(notification.type)}</div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-sm">{notification.title}</p>
                          <p className="text-sm text-muted-foreground">
                            {notification.message}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={() => deleteNotification(notification.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">
                          {formatTimestamp(notification.timestamp)}
                        </span>
                        {!notification.read && (
                          <Button
                            variant="link"
                            size="sm"
                            className="h-auto p-0 text-xs"
                            onClick={() => markAsRead(notification.id)}
                          >
                            Mark as read
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        {notifications.length > 0 && (
          <div className="p-2 border-t">
            <Button
              variant="ghost"
              size="sm"
              className="w-full"
              onClick={clearAll}
            >
              Clear all notifications
            </Button>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}