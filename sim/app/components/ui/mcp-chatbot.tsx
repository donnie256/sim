// components/ChatBot.tsx
'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'


interface Message {
  role: 'user' | 'bot'
  content: string
}

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim()) return
    const newMessages: Message[] = [...messages, { role: 'user' as const, content: input }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          model: "mistralai/mistral-small-3.1-24b-instruct:free", 
        }),
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
    <div className="w-full h-full p-6 flex flex-col justify-end">
      <Card className="w-full max-w-4xl mx-auto flex flex-col h-[80vh]">
        <div className="flex items-center justify-between p-4">
          <CardHeader className="p-0">
            <CardTitle>AI Assistant</CardTitle>
          </CardHeader>
        </div>

        <CardContent className="space-y-3 flex-1 overflow-y-auto px-4">
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
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          ))}
        </CardContent>

        <div className="p-4 border-t">
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
        </div>
      </Card>
    </div>
  )
}
