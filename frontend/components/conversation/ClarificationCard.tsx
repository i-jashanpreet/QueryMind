import React, { useState } from "react";
import { ClarificationResponse } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";

interface ClarificationCardProps {
  clarification: ClarificationResponse;
  onSubmit: (answer: string) => void;
  disabled?: boolean;
}

export default function ClarificationCard({ clarification, onSubmit, disabled }: ClarificationCardProps) {
  const [freeText, setFreeText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (freeText.trim() && !disabled) {
      onSubmit(freeText.trim());
    }
  };

  return (
    <div className="flex flex-col gap-4 bg-background border border-border/60 rounded-xl p-5 shadow-sm max-w-lg w-full">
      <div className="space-y-1">
        <h4 className="font-medium text-foreground">Let's clarify that</h4>
        {clarification.question && (
          <p className="text-sm text-muted-foreground">{clarification.question}</p>
        )}
      </div>

      {clarification.options.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
          {clarification.options.map((opt, i) => (
            <Button
              key={i}
              variant="outline"
              disabled={disabled}
              className="justify-start h-auto py-2.5 px-3 text-left font-normal bg-secondary/30 hover:bg-secondary/60 border-border/40"
              onClick={() => onSubmit(opt.value)}
            >
              {opt.label}
            </Button>
          ))}
        </div>
      )}

      <div className="relative mt-2 flex items-center">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border/40" />
        </div>
        <div className="relative flex justify-center text-xs uppercase w-full">
          <span className="bg-background px-2 text-muted-foreground/60">Or type your answer</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={freeText}
          onChange={(e) => setFreeText(e.target.value)}
          disabled={disabled}
          placeholder="Type your clarification..."
          className="flex-1 bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500/50"
        />
        <Button 
          type="submit" 
          disabled={disabled || !freeText.trim()} 
          size="icon" 
          className="shrink-0 bg-blue-600 hover:bg-blue-700"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
