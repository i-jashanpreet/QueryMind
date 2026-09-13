import React, { useState } from "react";
import { Send, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ComposerProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

const examplePrompts = [
  "Show me the top 5 products by revenue",
  "How many new users signed up this month?",
  "What is the average order value by region?",
];

export default function Composer({ onSubmit, isLoading }: ComposerProps) {
  const [text, setText] = useState("");

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (text.trim() && !isLoading) {
      onSubmit(text.trim());
      setText("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-6 mt-auto">
      <div className="flex flex-wrap gap-2 justify-center mb-6">
        {examplePrompts.map((prompt, i) => (
          <Button
            key={i}
            variant="secondary"
            onClick={() => {
              setText(prompt);
            }}
            disabled={isLoading}
            className="rounded-full text-xs bg-secondary/50 hover:bg-secondary text-secondary-foreground font-normal border border-border/40"
          >
            <Sparkles className="h-3 w-3 mr-2 text-blue-500" />
            {prompt}
          </Button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="relative flex items-center w-full bg-background border border-border rounded-2xl shadow-sm focus-within:border-blue-500/50 focus-within:ring-1 focus-within:ring-blue-500/50 transition-all p-1">
        <textarea
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder={isLoading ? "QueryMind is thinking..." : "Ask your data anything..."}
          className="w-full bg-transparent resize-none border-0 focus:ring-0 p-3 text-sm placeholder:text-muted-foreground outline-none disabled:opacity-50"
          style={{ minHeight: "52px" }}
        />
        <Button 
          type="submit" 
          disabled={!text.trim() || isLoading} 
          size="icon" 
          className="h-10 w-10 shrink-0 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-sm ml-2 mr-1 disabled:opacity-50"
        >
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </Button>
      </form>
      <div className="text-center mt-3">
         <span className="text-[10px] text-muted-foreground/60 uppercase tracking-widest font-semibold">Press Enter to Run</span>
      </div>
    </div>
  );
}
