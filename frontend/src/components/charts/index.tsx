"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

// NOTE: Install recharts: npm install recharts
// This file provides chart wrapper components that will work with Recharts

interface BaseChartProps {
  title?: string;
  description?: string;
  className?: string;
}

// Line Chart Component
export interface LineChartData {
  name: string;
  [key: string]: string | number;
}

interface LineChartProps extends BaseChartProps {
  data: LineChartData[];
  dataKeys: string[];
  xAxisKey?: string;
  colors?: string[];
  height?: number;
}

export function LineChart({
  title,
  description,
  data: _data,
  dataKeys: _dataKeys,
  xAxisKey: _xAxisKey = "name",
  colors: _colors = ["#8884d8", "#82ca9d", "#ffc658"],
  height: _height = 300,
  className,
}: LineChartProps) {
  return (
    <Card className={className}>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent>
        <div className="h-[300px] w-full">
          <p className="text-muted-foreground text-sm text-center py-12">
            Line Chart Placeholder
            <br />
            <span className="text-xs">Install: npm install recharts</span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// Bar Chart Component
export interface BarChartData {
  name: string;
  [key: string]: string | number;
}

interface BarChartProps extends BaseChartProps {
  data: BarChartData[];
  dataKeys: string[];
  xAxisKey?: string;
  colors?: string[];
  height?: number;
  layout?: "vertical" | "horizontal";
}

export function BarChart({
  title,
  description,
  data: _data,
  dataKeys: _dataKeys,
  xAxisKey: _xAxisKey = "name",
  colors: _colors = ["#8884d8", "#82ca9d", "#ffc658"],
  height: _height = 300,
  layout: _layout = "horizontal",
  className,
}: BarChartProps) {
  return (
    <Card className={className}>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent>
        <div className="h-[300px] w-full">
          <p className="text-muted-foreground text-sm text-center py-12">
            Bar Chart Placeholder
            <br />
            <span className="text-xs">Install: npm install recharts</span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// Pie Chart Component
export interface PieChartData {
  name: string;
  value: number;
  fill?: string;
}

interface PieChartProps extends BaseChartProps {
  data: PieChartData[];
  colors?: string[];
  height?: number;
  showLegend?: boolean;
  innerRadius?: number;
  outerRadius?: number;
}

export function PieChart({
  title,
  description,
  data: _data,
  colors: _colors = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"],
  height: _height = 300,
  showLegend: _showLegend = true,
  innerRadius: _innerRadius = 0,
  outerRadius: _outerRadius = 80,
  className,
}: PieChartProps) {
  return (
    <Card className={className}>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent>
        <div className="h-[300px] w-full flex items-center justify-center">
          <p className="text-muted-foreground text-sm text-center">
            Pie Chart Placeholder
            <br />
            <span className="text-xs">Install: npm install recharts</span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// Area Chart Component
export interface AreaChartData {
  name: string;
  [key: string]: string | number;
}

interface AreaChartProps extends BaseChartProps {
  data: AreaChartData[];
  dataKeys: string[];
  xAxisKey?: string;
  colors?: string[];
  height?: number;
  stacked?: boolean;
}

export function AreaChart({
  title,
  description,
  data: _data,
  dataKeys: _dataKeys,
  xAxisKey: _xAxisKey = "name",
  colors: _colors = ["#8884d8", "#82ca9d", "#ffc658"],
  height: _height = 300,
  stacked: _stacked = false,
  className,
}: AreaChartProps) {
  return (
    <Card className={className}>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent>
        <div className="h-[300px] w-full">
          <p className="text-muted-foreground text-sm text-center py-12">
            Area Chart Placeholder
            <br />
            <span className="text-xs">Install: npm install recharts</span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
}