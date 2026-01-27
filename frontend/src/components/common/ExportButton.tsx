"use client";

import { useState } from "react";
import { Download, FileText, FileSpreadsheet, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast";

interface ExportButtonProps {
  data: any[];
  filename?: string;
  csvHeaders?: string[];
  className?: string;
  variant?: "default" | "outline" | "ghost";
}

export function ExportButton({
  data,
  filename = "export",
  csvHeaders,
  className,
  variant = "outline",
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const { toast } = useToast();

  const exportToCSV = async () => {
    setIsExporting(true);
    try {
      // Convert data to CSV format
      const headers = csvHeaders || (data.length > 0 ? Object.keys(data[0]) : []);
      const csvContent = [
        headers.join(","),
        ...data.map((row) =>
          headers.map((header) => {
            const value = row[header] ?? "";
            // Escape commas and quotes
            const escaped = String(value).replace(/"/g, '""');
            return `"${escaped}"`;
          }).join(",")
        ),
      ].join("\n");

      // Create blob and download
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${filename}_${new Date().toISOString().split("T")[0]}.csv`;
      link.click();

      toast({
        title: "Export Successful",
        description: `Downloaded ${data.length} rows as CSV`,
      });
    } catch (error) {
      toast({
        title: "Export Failed",
        description: "Unable to export data to CSV",
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  const exportToPDF = async () => {
    setIsExporting(true);
    try {
      // Note: Requires jspdf library
      // npm install jspdf
      toast({
        title: "PDF Export",
        description: "PDF export requires jspdf library. Install: npm install jspdf",
      });

      // Basic implementation placeholder
      // Uncomment when jspdf is installed:
      /*
      const { jsPDF } = await import('jspdf');
      const doc = new jsPDF();
      
      doc.text(filename, 10, 10);
      doc.text(`Total Records: ${data.length}`, 10, 20);
      
      // Add data rows
      let y = 30;
      data.slice(0, 20).forEach((row, index) => {
        const text = JSON.stringify(row, null, 2);
        doc.text(`${index + 1}. ${text}`, 10, y);
        y += 10;
      });
      
      doc.save(`${filename}_${new Date().toISOString().split('T')[0]}.pdf`);
      
      toast({
        title: 'Export Successful',
        description: `Downloaded as PDF`,
      });
      */
    } catch (error) {
      toast({
        title: "Export Failed",
        description: "Unable to export data to PDF",
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  const exportToJSON = async () => {
    setIsExporting(true);
    try {
      const jsonContent = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonContent], { type: "application/json" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${filename}_${new Date().toISOString().split("T")[0]}.json`;
      link.click();

      toast({
        title: "Export Successful",
        description: `Downloaded ${data.length} rows as JSON`,
      });
    } catch (error) {
      toast({
        title: "Export Failed",
        description: "Unable to export data to JSON",
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  };

  if (data.length === 0) {
    return (
      <Button variant={variant} className={className} disabled>
        <Download className="h-4 w-4 mr-2" />
        Export (No Data)
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} className={className} disabled={isExporting}>
          {isExporting ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Download className="h-4 w-4 mr-2" />
          )}
          Export ({data.length})
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Export Format</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={exportToCSV}>
          <FileSpreadsheet className="h-4 w-4 mr-2" />
          Export as CSV
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToJSON}>
          <FileText className="h-4 w-4 mr-2" />
          Export as JSON
        </DropdownMenuItem>
        <DropdownMenuItem onClick={exportToPDF}>
          <FileText className="h-4 w-4 mr-2" />
          Export as PDF
          <span className="text-xs text-muted-foreground ml-2">(Requires jspdf)</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}