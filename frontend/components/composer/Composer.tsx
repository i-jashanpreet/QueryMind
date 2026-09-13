import React from "react";
import { Send, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const examplePrompts = [
  "Show me the top 5 products by revenue",
  "How many new users signed up this month?",
  "What is the average order value by region?",
];

export default function Composer() {
  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-6 mt-auto">
      <div className="flex flex-wrap gap-2 justify-center mb-6">
        {examplePrompts.map((prompt, i) => (
          <Button
            key={i}
            variant="secondary"
            className="rounded-full text-xs bg-secondary/50 hover:bg-secondary text-secondary-foreground font-normal border border-border/40"
          >
            <Sparkles className="h-3 w-3 mr-2 text-blue-500" />
            {prompt}
          </Button>
        ))}
      </div>

      <div className="relative flex items-center w-full bg-background border border-border rounded-2xl shadow-sm focus-within:border-blue-500/50 focus-within:ring-1 focus-within:ring-blue-500/50 transition-all p-1">
        <textarea
          rows={1}
          placeholder="Ask your data anything..."
          className="w-full bg-transparent resize-none border-0 focus:ring-0 p-3 text-sm placeholder:text-muted-foreground outline-none"
          style={{ minHeight: "52px" }}
        />
        <Button size="icon" className="h-10 w-10 shrink-0 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-sm ml-2 mr-1">
          <Send className="h-4 w-4" />
        </Button>
      </div>
      <div className="text-center mt-3">
         <span className="text-[10px] text-muted-foreground/60 uppercase tracking-widest font-semibold">Press Enter to Run</span>
      </div>
    </div>
  );
}
