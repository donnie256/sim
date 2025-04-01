# --- email_agent.py ---

from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable, RunnableLambda
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import tool
from langsmith import traceable
from dotenv import load_dotenv
import os
import re
from gmail_handler import send_email_internal

load_dotenv()

# ----------------------
# Shared Agent State
# ----------------------
class AgentState(dict):
    pass

# ----------------------
# Email extraction helper
# ----------------------
def extract_email_parts(text: str):
    to_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    subject_match = re.search(r'subject ["\u201c](.+?)["\u201d]', text, re.IGNORECASE)
    body_match = re.search(r'body ["\u201c](.+?)["\u201d]', text, re.IGNORECASE)

    return {
        "to": to_match.group(0) if to_match else "your-email@example.com",
        "subject": subject_match.group(1) if subject_match else "Subject from AI",
        "body": body_match.group(1) if body_match else text
    }

# ----------------------
# Gmail MCP Tool
# ----------------------
def send_email_tool(to: str, subject: str, body: str) -> str:
    try:
        print(f"\U0001F4E4 Sending email directly: {to} | {subject}")
        email_id = send_email_internal(to, subject, body)
        return f"\u2705 Email sent to {to} (ID: {email_id})"
    except Exception as e:
        print(f"\u274C Failed to send email: {e}")
        return f"\u274C Failed to send email: {str(e)}"

# ----------------------
# LLM Agent
# ----------------------
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="mistralai/mistral-small-3.1-24b-instruct:free"
)

class LangAgent(Runnable):
    def invoke(self, state: AgentState, config=None) -> AgentState:
        messages = state.get("messages", [])
        user_msg = messages[-1].content.lower()

        # Step 1: Detect email intent
        should_send_email = any(keyword in user_msg for keyword in ["send email", "send an email", "email"])
        extracted = None

        if should_send_email:
            try:
                extracted = extract_email_parts(messages[-1].content)
                if extracted and all(k in extracted for k in ("to", "subject", "body")):
                    print(f"\U0001F4E7 Extracted email details: {extracted}")
            except Exception as e:
                print(f"\u274C Email extraction error: {e}")

        # Step 2: Run the LLM to keep chatbot behavior
        result = llm.invoke(messages)
        messages.append(result)

        # Step 3: Attach email parts to state if present
        new_state = AgentState({"messages": messages})
        if extracted:
            new_state["to"] = extracted["to"]
            new_state["subject"] = extracted["subject"]
            new_state["body"] = extracted["body"]

        return new_state

# ----------------------
# Tool decision logic
# ----------------------
def should_send_email(state: AgentState) -> str:
    if all(k in state for k in ("to", "subject", "body")):
        print(f"\U0001F916 should_send_email check — state keys: {list(state.keys())}")
        return "send_email"
    return END

# ----------------------
# LangGraph
# ----------------------
graph = StateGraph(AgentState)
graph.add_node("agent", LangAgent())
graph.add_node("send_email", RunnableLambda(lambda state: AgentState({
    **state,
    "messages": state["messages"] + [AIMessage(content=send_email_tool(
        to=state["to"],
        subject=state["subject"],
        body=state["body"]
    ))]
})))

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_send_email)
graph.add_edge("send_email", END)

email_agent = graph.compile()

# ----------------------
# External entrypoint
# ----------------------
@traceable(name="run_email_agent")
def run_email_agent(user_input: str):
    initial_messages = [
        SystemMessage(content="You are a helpful AI assistant that can also send emails when asked. "
                              "If the user provides an email request, extract the recipient (to), subject, "
                              "and body. You do not need to explain how to send the email manually."),
        HumanMessage(content=user_input)
    ]
    result = email_agent.invoke({"messages": initial_messages})
    return result["messages"][-1].content
