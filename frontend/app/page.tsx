"use client";

import React, { useState, useRef, useEffect } from "react";
import AppLayout from "@/components/layout/AppLayout";
import Composer from "@/components/composer/Composer";
import Message from "@/components/conversation/Message";
import ClarificationCard from "@/components/conversation/ClarificationCard";
import ResultTable from "@/components/conversation/ResultTable";
import SqlViewer from "@/components/conversation/SqlViewer";
import { Download, Share, UserCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { postQuery } from "@/lib/api";
import { QueryResponse } from "@/types/api";

type MessageItem = {
  id: string;
  role: "user" | "assistant";
  content?: string;
  response?: QueryResponse;
  error?: string;
};

export default function Home() {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleQuery = async (question: string) => {
    // Add user message
    const userMsg: MessageItem = { id: Date.now().toString(), role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const data = await postQuery(question, conversationId);
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }
      
      const assistantMsg: MessageItem = { 
        id: (Date.now() + 1).toString(), 
        role: "assistant", 
        response: data 
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: MessageItem = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        error: err.message || "An unknown error occurred",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

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

        {/* Main Workspace */}
        <main className="flex-1 flex flex-col relative overflow-hidden">
          
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center p-6">
              <div className="text-center mb-8 max-w-lg mt-auto pb-12">
                <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-blue-500/20 shadow-[0_0_40px_rgba(37,99,235,0.15)]">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg"></div>
                </div>
                <h2 className="text-3xl font-semibold text-foreground mb-3 tracking-tight">Ask your data anything.</h2>
                <p className="text-muted-foreground text-sm">
                  Turn natural language into SQL, insights and answers.
                </p>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto p-6" ref={scrollRef}>
              <div className="max-w-4xl mx-auto space-y-6 pb-20">
                {messages.map((msg) => (
                  <Message key={msg.id} role={msg.role}>
                    {msg.role === "user" ? (
                      msg.content
                    ) : msg.error ? (
                      <div className="flex items-start gap-2 text-red-500">
                        <AlertCircle className="h-5 w-5 mt-0.5" />
                        <div>
                          <p className="font-semibold">Something went wrong</p>
                          <p className="text-sm mt-1">{msg.error}</p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col gap-4 w-full">
                        {msg.response?.needs_clarification && msg.response.clarification && (
                          <ClarificationCard 
                            clarification={msg.response.clarification} 
                            onSubmit={handleQuery} 
                            disabled={isLoading || messages[messages.length - 1].id !== msg.id}
                          />
                        )}
                        
                        {!msg.response?.needs_clarification && (
                          <>
                            <div className="text-[15px] leading-relaxed">Here are the results.</div>
                            {msg.response?.sql && <SqlViewer sql={msg.response.sql} />}
                            {msg.response?.results && <ResultTable results={msg.response.results} />}
                          </>
                        )}
                      </div>
                    )}
                  </Message>
                ))}
                {isLoading && (
                  <Message role="assistant">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <div className="h-4 w-4 border-2 border-muted-foreground border-t-transparent rounded-full animate-spin"></div>
                      QueryMind is thinking...
                    </div>
                  </Message>
                )}
              </div>
            </div>
          )}

          <div className="w-full bg-gradient-to-t from-background via-background/90 to-transparent pt-6">
            <Composer onSubmit={handleQuery} isLoading={isLoading} />
          </div>
        </main>
      </div>
    </AppLayout>
  );
}
