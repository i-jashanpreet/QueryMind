"use client";

import React, { useState } from "react";
import Sidebar from "@/components/sidebar/Sidebar";
import RightInspector from "@/components/inspector/RightInspector";
import { Sheet, SheetContent, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-foreground">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex h-full w-[260px] flex-col border-r border-border/40 bg-sidebar/50 backdrop-blur-xl">
        <Sidebar />
      </div>

      {/* Mobile Sidebar (Sheet) */}
      <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
        <SheetContent side="left" className="p-0 w-[260px] border-border/40 bg-sidebar">
          <SheetTitle className="sr-only">Menu</SheetTitle>
          <SheetDescription className="sr-only">Navigation Menu</SheetDescription>
          <Sidebar />
        </SheetContent>
      </Sheet>

      {/* Main Workspace */}
      <div className="flex flex-1 flex-col overflow-hidden relative bg-background">
        {/* Mobile Header for Menu Toggle */}
        <div className="md:hidden flex items-center justify-between p-4 border-b border-border/40 bg-background absolute top-0 w-full z-10">
          <div className="font-semibold text-lg flex items-center gap-2">
            <div className="w-5 h-5 bg-blue-600 rounded-sm"></div>
            QueryMind
          </div>
          <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(true)}>
            <Menu className="w-5 h-5" />
          </Button>
        </div>
        
        {/* Workspace Content */}
        <div className="flex-1 overflow-hidden pt-[60px] md:pt-0">
          {children}
        </div>
      </div>

      {/* Desktop Right Inspector */}
      <div className="hidden xl:flex h-full w-[280px] flex-col border-l border-border/40 bg-sidebar/30 backdrop-blur-sm">
        <RightInspector />
      </div>
    </div>
  );
}
