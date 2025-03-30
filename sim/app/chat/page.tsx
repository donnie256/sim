'use client'

import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import ChatBot from '@/components/ui/mcp-chatbot'
import { Sidebar } from '../w/components/sidebar/sidebar'

export default function ChatTabsPage() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="ml-14 flex-1 p-4">
        <Tabs defaultValue="chatbot" className="w-full max-w-5xl mx-auto">
          <TabsList>
            <TabsTrigger value="chatbot">Chatbot</TabsTrigger>
          </TabsList>

          <TabsContent value="chatbot">
            <ChatBot />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
