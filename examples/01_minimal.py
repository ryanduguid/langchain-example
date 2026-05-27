"""
Minimal LangChain + OpenAccountants example.

Asks the agent: "I'm a Maltese freelancer earning EUR 45,000 from foreign
clients. What VAT obligations do I have?" — and the agent calls the
OpenAccountants MCP server to fetch the right skills and answer.

Run:
    pip install langchain-mcp-adapters langchain-anthropic
    export ANTHROPIC_API_KEY=...
    python examples/01_minimal.py
"""

import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main() -> None:
    # Connect to the public OpenAccountants MCP server. No auth required.
    client = MultiServerMCPClient(
        {
            "openaccountants": {
                "transport": "streamable_http",
                "url": "https://www.openaccountants.com/api/mcp",
            }
        }
    )

    tools = await client.get_tools()
    print(f"Loaded {len(tools)} tools from OpenAccountants MCP:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:80]}…")
    print()

    # Build a LangChain agent that can call those tools.
    agent = create_agent(
        "anthropic:claude-sonnet-4-5",
        tools,
        system_message=(
            "You are a tax assistant. When a user asks a tax or accounting "
            "question, first call `start` to scope the workflow, then "
            "`get_skill` to load the relevant accountant-verified skill, "
            "then walk the user through it. Always cite the skill slug and "
            "the named verifier in the answer."
        ),
    )

    question = (
        "I'm a Maltese freelancer earning EUR 45,000 from foreign B2B "
        "clients. What VAT obligations do I have, and is there a "
        "small-enterprise scheme I should consider?"
    )
    print(f"User: {question}\n")

    response = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
    print("Agent:")
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
