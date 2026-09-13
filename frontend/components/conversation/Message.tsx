import React from "react";
import { User, Sparkles } from "lucide-react";

interface MessageProps {
  role: "user" | "assistant";
  children: React.ReactNode;
}

export default function Message({ role, children }: MessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-6`}>
      <div className={`flex gap-3 max-w-[85%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        <div className="flex-shrink-0 mt-1">
          {isUser ? (
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600/20 text-blue-500 border border-blue-500/30">
              <User className="h-4 w-4" />
            </div>
          ) : (
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white shadow-sm">
              <Sparkles className="h-4 w-4" />
            </div>
          )}
        </div>
        
        <div className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}>
          {typeof children === "string" ? (
             <div className={`px-4 py-3 rounded-2xl text-[15px] leading-relaxed shadow-sm ${
                isUser 
                ? "bg-secondary/60 text-secondary-foreground rounded-tr-sm border border-border/40" 
                : "bg-background border border-border/60 text-foreground rounded-tl-sm"
              }`}>
               {children}
             </div>
          ) : (
            children
          )}
        </div>
      </div>
    </div>
  );
}
