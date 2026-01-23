"use client";

import { LucideIcon, TrendingUp, TrendingDown, Minus, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface KPICardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: number;
    label?: string;
    isPositive?: boolean;
  };
  comparison?: {
    label: string;
    value: string;
  };
  link?: string;
  onClick?: () => void;
  className?: string;
  iconClassName?: string;
  sparklineData?: number[]; // Simple array for mini trend visualization
}

export function KPICard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  comparison,
  link,
  onClick,
  className,
  iconClassName,
  sparklineData,
}: KPICardProps) {
  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend.value > 0) return <TrendingUp className="h-4 w-4" />;
    if (trend.value < 0) return <TrendingDown className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
  };

  const getTrendColor = () => {
    if (!trend) return "";
    if (trend.isPositive === undefined) {
      return trend.value > 0 ? "text-green-600" : trend.value < 0 ? "text-red-600" : "text-gray-600";
    }
    return trend.isPositive ? "text-green-600" : "text-red-600";
  };

  const CardWrapper = link ? Link : "div";
  const wrapperProps: any = link ? { href: link } : onClick ? { onClick } : {};

  const isClickable = link || onClick;

  return (
    <CardWrapper {...wrapperProps}>
      <Card
        className={cn(
          "transition-all duration-200",
          isClickable && "cursor-pointer hover:shadow-lg hover:scale-[1.02]",
          className
        )}
      >
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <div className={cn("p-2 rounded-lg bg-primary/10", iconClassName)}>
            <Icon className="h-4 w-4 text-primary" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {/* Main Value */}
            <div className="flex items-baseline justify-between">
              <div className="text-2xl font-bold">{value}</div>
              {trend && (
                <div className={cn("flex items-center gap-1 text-xs font-medium", getTrendColor())}>
                  {getTrendIcon()}
                  <span>{Math.abs(trend.value)}%</span>
                </div>
              )}
            </div>

            {/* Description */}
            {description && <p className="text-xs text-muted-foreground">{description}</p>}

            {/* Trend Label */}
            {trend?.label && (
              <p className="text-xs text-muted-foreground">{trend.label}</p>
            )}

            {/* Comparison */}
            {comparison && (
              <div className="flex items-center justify-between pt-2 border-t">
                <span className="text-xs text-muted-foreground">{comparison.label}</span>
                <Badge variant="secondary" className="text-xs">
                  {comparison.value}
                </Badge>
              </div>
            )}

            {/* Simple Sparkline */}
            {sparklineData && sparklineData.length > 0 && (
              <div className="flex items-end gap-0.5 h-8 mt-2">
                {sparklineData.map((value, index) => {
                  const maxValue = Math.max(...sparklineData);
                  const heightPercent = (value / maxValue) * 100;
                  return (
                    <div
                      key={index}
                      className="flex-1 bg-primary/20 rounded-sm transition-all hover:bg-primary/40"
                      style={{ height: `${heightPercent}%` }}
                    />
                  );
                })}
              </div>
            )}

            {/* Click-through indicator */}
            {isClickable && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground pt-2 group-hover:text-primary transition-colors">
                <span>View details</span>
                <ArrowRight className="h-3 w-3" />
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </CardWrapper>
  );
}