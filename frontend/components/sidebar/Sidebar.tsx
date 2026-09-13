import React from "react";
import { MessageSquare, Save, Database, Settings, Plus, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

const recentConversations = [
  "Top products by revenue",
  "Revenue analysis",
  "Monthly sales",
  "Customer analysis",
];

export default function Sidebar() {
  return (
    <div className="flex h-full flex-col p-4 space-y-4">
      {/* Brand */}
      <div className="flex items-center gap-3 px-2 py-1">
        <div className="flex h-6 w-6 items-center justify-center rounded-md bg-blue-600 text-white font-bold text-xs">
          QM
        </div>
        <span className="font-semibold text-lg tracking-tight">QueryMind</span>
      </div>

      {/* New Query Action */}
      <Button className="w-full justify-start gap-2 bg-blue-600 hover:bg-blue-700 text-white" size="sm">
        <Plus className="h-4 w-4" />
        New Query
      </Button>

      <ScrollArea className="flex-1 -mx-2 px-2">
        <div className="space-y-4">
          {/* Main Navigation */}
          <div className="space-y-1">
            <Button variant="ghost" className="w-full justify-start gap-2 h-9 px-2 font-medium bg-sidebar-accent">
              <MessageSquare className="h-4 w-4" />
              Conversations
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2 h-9 px-2 text-muted-foreground hover:text-foreground">
              <Save className="h-4 w-4" />
              Saved Queries
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2 h-9 px-2 text-muted-foreground hover:text-foreground">
              <Database className="h-4 w-4" />
              Database
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2 h-9 px-2 text-muted-foreground hover:text-foreground">
              <Settings className="h-4 w-4" />
              Settings
            </Button>
          </div>

          <Separator className="bg-border/50" />

          {/* Recent */}
          <div className="space-y-1">
            <h4 className="px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Recent
            </h4>
            {recentConversations.map((conv, i) => (
              <Button
                key={i}
                variant="ghost"
                className="w-full justify-start h-8 px-2 text-sm text-muted-foreground hover:text-foreground font-normal truncate"
              >
                {conv}
              </Button>
            ))}
          </div>
        </div>
      </ScrollArea>

      {/* User Section */}
      <div className="mt-auto pt-4 border-t border-border/50">
        <Button variant="ghost" className="w-full justify-start gap-2 h-10 px-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-sidebar-accent border border-border">
            <User className="h-4 w-4 text-muted-foreground" />
          </div>
          <span className="text-sm font-medium">User Account</span>
        </Button>
      </div>
    </div>
  );
}
