import React from "react";
import { Info, Database } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

// For this milestone, the /query endpoint doesn't return the full analysis.
// We only have real data if it is provided. Otherwise show "Not available".
export default function RightInspector() {
  return (
    <div className="flex h-full flex-col p-4 space-y-6">
      <div className="flex items-center gap-2 px-1">
        <Info className="h-4 w-4 text-muted-foreground" />
        <h3 className="font-medium text-sm">Query Analysis</h3>
      </div>

      <ScrollArea className="flex-1 -mx-2 px-2">
        <div className="space-y-8">
          
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-blue-500"></div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Intent
              </h4>
            </div>
            <div className="px-3">
              <span className="text-sm text-muted-foreground italic">Not available for this query</span>
            </div>
          </div>

          <Separator className="bg-border/50" />

          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Database className="h-3.5 w-3.5 text-muted-foreground" />
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Relevant Schema
              </h4>
            </div>
            <div className="px-3">
              <span className="text-sm text-muted-foreground italic">Not available for this query</span>
            </div>
          </div>

        </div>
      </ScrollArea>
    </div>
  );
}
