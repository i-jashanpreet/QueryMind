import React from "react";
import { Info, Database } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

export default function RightInspector() {
  return (
    <div className="flex h-full flex-col p-4 space-y-6">
      <div className="flex items-center gap-2 px-1">
        <Info className="h-4 w-4 text-muted-foreground" />
        <h3 className="font-medium text-sm">Query Analysis</h3>
      </div>

      <ScrollArea className="flex-1 -mx-2 px-2">
        <div className="space-y-8">
          
          {/* Intent Section Placeholder */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-blue-500"></div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Intent
              </h4>
            </div>
            <div className="space-y-2 px-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Metric</span>
                <span className="text-muted-foreground/50">—</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Entity</span>
                <span className="text-muted-foreground/50">—</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Limit</span>
                <span className="text-muted-foreground/50">—</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">Sort</span>
                <span className="text-muted-foreground/50">—</span>
              </div>
            </div>
          </div>

          <Separator className="bg-border/50" />

          {/* Schema Section Placeholder */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Database className="h-3.5 w-3.5 text-muted-foreground" />
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Relevant Schema
              </h4>
            </div>
            <div className="px-3 space-y-2">
              <div className="text-sm text-muted-foreground flex items-center gap-2">
                <div className="h-1 w-1 rounded-full bg-border"></div>
                products
              </div>
              <div className="text-sm text-muted-foreground flex items-center gap-2">
                <div className="h-1 w-1 rounded-full bg-border"></div>
                order_items
              </div>
              <div className="text-sm text-muted-foreground flex items-center gap-2">
                <div className="h-1 w-1 rounded-full bg-border"></div>
                orders
              </div>
            </div>
          </div>

          <div className="mt-8 px-3 text-center">
            <p className="text-xs text-muted-foreground/60 italic">
              Query analysis will appear here after you run a query.
            </p>
          </div>

        </div>
      </ScrollArea>
    </div>
  );
}
