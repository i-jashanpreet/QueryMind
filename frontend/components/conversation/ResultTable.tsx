import React from "react";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

interface ResultTableProps {
  results: Record<string, any>[];
}

export default function ResultTable({ results }: ResultTableProps) {
  if (!results || results.length === 0) {
    return (
      <div className="p-8 text-center text-sm text-muted-foreground bg-background border border-border/40 rounded-xl">
        No results found for this query.
      </div>
    );
  }

  const columns = Object.keys(results[0]);

  return (
    <div className="rounded-xl border border-border/60 bg-background overflow-hidden shadow-sm">
      <ScrollArea className="w-full max-w-[800px] whitespace-nowrap">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted-foreground uppercase bg-secondary/40">
            <tr>
              {columns.map((col) => (
                <th key={col} className="px-4 py-3 font-medium tracking-wider border-b border-border/50">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {results.map((row, i) => (
              <tr key={i} className="hover:bg-secondary/20 transition-colors">
                {columns.map((col) => (
                  <td key={col} className="px-4 py-2.5 text-foreground max-w-[250px] truncate">
                    {row[col] !== null ? String(row[col]) : (
                      <span className="text-muted-foreground/50 italic">null</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  );
}
