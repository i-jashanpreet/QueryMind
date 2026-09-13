import React, { useState } from "react";
import { Check, Copy, Database } from "lucide-react";
import { Button } from "@/components/ui/button";

interface SqlViewerProps {
  sql: string;
}

export default function SqlViewer({ sql }: SqlViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl border border-border/60 bg-[#1e1e1e] overflow-hidden shadow-sm my-2 w-full max-w-2xl">
      <div className="flex items-center justify-between px-4 py-2 bg-black/40 border-b border-white/10">
        <div className="flex items-center gap-2 text-xs font-medium text-white/70">
          <Database className="h-3.5 w-3.5" />
          Generated SQL
        </div>
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-7 gap-1.5 text-white/70 hover:text-white hover:bg-white/10 px-2"
          onClick={handleCopy}
        >
          {copied ? <Check className="h-3.5 w-3.5 text-green-400" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? "Copied" : "Copy SQL"}
        </Button>
      </div>
      <div className="p-4 overflow-x-auto text-sm text-[#d4d4d4] font-mono leading-relaxed whitespace-pre">
        {sql}
      </div>
    </div>
  );
}
