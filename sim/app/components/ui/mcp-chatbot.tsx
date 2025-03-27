// components/ChatBot.tsx
'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface Message {
  role: 'user' | 'bot'
  content: string
}

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(true)

  const handleSend = async () => {
    if (!input.trim()) return
    const newMessages: Message[] = [...messages, { role: 'user' as const, content: input }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      })

      if (!res.ok) {
        throw new Error('Failed to fetch response from server')
      }

      const data = await res.json()
      setMessages((prev) => [...prev, { role: 'bot', content: data.reply }])
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'bot', content: 'Oops! Something went wrong.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed bottom-4 right-4 w-full max-w-md z-50">
      <Card className="w-full p-4 space-y-4">
        <div className="flex items-center justify-between">
          <CardHeader className="p-0">
            <CardTitle>AI Assistant</CardTitle>
          </CardHeader>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(!isOpen)}
            aria-label={isOpen ? 'Minimize chat' : 'Expand chat'}
          >
            {isOpen ? <ChevronDown className="h-5 w-5" /> : <ChevronUp className="h-5 w-5" />}
          </Button>
        </div>

        {isOpen && (
          <>
            <CardContent className="space-y-3 max-h-[60vh] overflow-y-auto">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={cn(
                    'p-2 rounded-md whitespace-pre-wrap text-sm',
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground self-end text-right'
                      : 'bg-muted text-muted-foreground self-start text-left'
                  )}
                >
                  {msg.content}
                </div>
              ))}
            </CardContent>
            <div className="flex gap-2">
              <textarea
                className="flex-grow resize-none rounded-md border px-3 py-2 text-sm bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:opacity-50"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                placeholder="Ask me anything..."
                disabled={loading}
                rows={1}
              />
              <Button onClick={handleSend} disabled={loading}>
                {loading ? '...' : 'Send'}
              </Button>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
