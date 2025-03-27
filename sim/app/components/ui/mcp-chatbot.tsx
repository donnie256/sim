// components/ChatBot.tsx
'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input' // You may need to add this if not in your UI
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

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
        <CardHeader>
          <CardTitle>AI Assistant</CardTitle>
        </CardHeader>
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
          <Input
            className="flex-grow"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask me anything..."
            disabled={loading}
          />
          <Button onClick={handleSend} disabled={loading}>
            {loading ? '...' : 'Send'}
          </Button>
        </div>
      </Card>
    </div>
  )
}
