import React from "react";
import AppLayout from "@/components/layout/AppLayout";
import Composer from "@/components/composer/Composer";
import { Download, Share, UserCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <AppLayout>
      <div className="flex flex-col h-full">
        {/* Top Header */}
        <header className="hidden md:flex items-center justify-between px-6 py-4 border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-10 sticky top-0">
          <div className="flex items-center gap-4">
            <h1 className="font-semibold text-lg text-foreground tracking-tight">QueryMind</h1>
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 px-3 py-1.5 rounded-md border border-border/50">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
              PostgreSQL · querymind_prod
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="h-8 gap-2 border-border/50 bg-background">
              <Download className="h-3.5 w-3.5" />
              Export
            </Button>
            <Button variant="outline" size="sm" className="h-8 gap-2 border-border/50 bg-background">
              <Share className="h-3.5 w-3.5" />
              Share
            </Button>
            <div className="h-8 w-px bg-border/50 mx-1"></div>
            <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
              <UserCircle className="h-6 w-6 text-muted-foreground" />
            </Button>
          </div>
        </header>

        {/* Main Empty State */}
        <main className="flex-1 flex flex-col items-center justify-center p-6 relative">
          
          <div className="text-center mb-8 max-w-lg mt-auto pb-12">
            <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-blue-500/20 shadow-[0_0_40px_rgba(37,99,235,0.15)]">
               <div className="w-8 h-8 bg-blue-600 rounded-lg"></div>
            </div>
            <h2 className="text-3xl font-semibold text-foreground mb-3 tracking-tight">Ask your data anything.</h2>
            <p className="text-muted-foreground text-sm">
              Turn natural language into SQL, insights and answers.
            </p>
          </div>

          <Composer />
        </main>
      </div>
    </AppLayout>
  );
}
