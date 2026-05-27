"""
Compare tax treatment of the same income across multiple jurisdictions.

Real-world use: a remote worker or founder deciding where to incorporate.
The agent loads multiple country skills and computes effective rates
side-by-side.

Run:
    pip install langchain-mcp-adapters langchain-anthropic
    export ANTHROPIC_API_KEY=...
    python examples/03_compare_jurisdictions.py
"""

import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main() -> None:
    client = MultiServerMCPClient(
        {
            "openaccountants": {
                "transport": "streamable_http",
                "url": "https://www.openaccountants.com/api/mcp",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_agent(
        "anthropic:claude-sonnet-4-5",
        tools,
        system_message=(
            "You are a cross-border tax advisor. When asked to compare "
            "jurisdictions, load each country's income tax skill via "
            "get_skill, compute the effective tax rate at the given income, "
            "and produce a comparison table. Always include the verifier "
            "name and Calendly link from each skill's footer in the output."
        ),
    )

    prompt = (
        "I'm a EUR 200,000/year independent consultant choosing where to "
        "incorporate. Compare Malta, Ireland, and Portugal (with NHR/IFICI "
        "if applicable) at this income level. Show effective tax rate "
        "including corporate + personal layers if I take the income as "
        "salary vs dividends."
    )
    print(f"User: {prompt}\n")

    response = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    print("Agent:")
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
