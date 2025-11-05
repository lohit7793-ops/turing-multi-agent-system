# prototypes/langgraph-support-bot/app.py
from typing import TypedDict, Dict
from langgraph.graph import StateGraph, START, END

# ------------------ Tiny KB ------------------
KB: Dict[str, str] = {
    "reset password": "Go to Settings → Security → Reset Password. You’ll get a one-time link by email.",
    "shipping status": "Open Orders → Track to see real-time shipment updates.",
    "refund policy":  "Refunds are available within 30 days if unused and in original packaging."
}

def kb_lookup(q: str) -> str:
    """
    Token-based matcher:
      - order-independent (e.g., 'password reset' == 'reset password')
      - handles phrasing like 'reset my password'
      - simple synonym: 'pwd' => 'password'
    """
    import re
    q_tokens = set(re.findall(r"[a-z0-9]+", q.lower()))
    if "pwd" in q_tokens:
        q_tokens.add("password")
    for key, ans in KB.items():
        key_tokens = set(key.split())
        if key_tokens.issubset(q_tokens):
            return ans
    return "I couldn’t find that in the KB. Please try rephrasing or open a ticket."

# ------------------ Graph State ------------------
class SupportState(TypedDict):
    query: str     # user input
    route: str     # faq | refund | ticket | handoff
    result: str    # final text

# ------------------ Nodes ------------------
def router(state: SupportState) -> dict:
    q = state["query"].lower()
    if "refund" in q:
        r = "refund"
    elif "ticket" in q or "create a ticket" in q or "open a ticket" in q:
        r = "ticket"
    elif "complaint" in q or "legal" in q or "lawyer" in q:
        r = "handoff"
    else:
        r = "faq"
    return {"route": r}

def faq_tool(state: SupportState) -> dict:
    return {"result": f"[FAQ]\n{kb_lookup(state['query'])}"}

def refund_tool(state: SupportState) -> dict:
    import re
    m = re.search(r"\b(\d{5,})\b", state["query"])   # pick 5+ digit order ids
    order_id = m.group(1) if m else "UNKNOWN"
    return {"result": f"[REFUND]\nRefund initialized for order {order_id}. You’ll get a confirmation email."}

def ticket_tool(state: SupportState) -> dict:
    import random
    ticket_id = f"TKT-{random.randint(1000, 9999)}"
    return {"result": f"[TICKET]\nCreated ticket {ticket_id}. Our team will follow up shortly."}

def handoff_tool(state: SupportState) -> dict:
    return {"result": "[HANDOFF]\nThis needs a human agent. I’ve escalated your request to support."}

# ------------------ Build Graph ------------------
graph = StateGraph(SupportState)
graph.add_node("router", router)
graph.add_node("faq", faq_tool)
graph.add_node("refund", refund_tool)
graph.add_node("ticket", ticket_tool)
graph.add_node("handoff", handoff_tool)

graph.add_edge(START, "router")
graph.add_conditional_edges("router", lambda s: s["route"], {
    "faq": "faq", "refund": "refund", "ticket": "ticket", "handoff": "handoff"
})
for n in ("faq", "refund", "ticket", "handoff"):
    graph.add_edge(n, END)

app = graph.compile()

# ------------------ CLI ------------------
def main():
    print("Customer Support Bot (LangGraph) — type 'exit' to quit")
    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        out = app.invoke({"query": q, "route": "", "result": ""})
        print(f"\nRoute: {out['route']}\n{out['result']}\n")

if __name__ == "__main__":
    main()
