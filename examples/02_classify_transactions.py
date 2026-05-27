"""
Classify bank transactions using OpenAccountants jurisdiction-specific rules.

Real-world use: small businesses dump a CSV of bank transactions and want
each one categorized correctly for their tax filing. The agent loads the
right country's bookkeeping + VAT skill, then runs each transaction through it.

Run:
    pip install langchain-mcp-adapters langchain-anthropic
    export ANTHROPIC_API_KEY=...
    python examples/02_classify_transactions.py
"""

import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# Sample German freelancer transactions for January 2025
TRANSACTIONS = """
Date,Description,Amount EUR
2025-01-03,Server hosting Hetzner GmbH,-89.00
2025-01-05,Client invoice INV-2025-001 paid (Berlin SaaS GmbH),+4200.00
2025-01-08,Lunch with potential client - Restaurant Schwarzwald,-67.50
2025-01-10,Adobe Creative Cloud subscription (US),-59.99
2025-01-15,Coworking space membership Mindspace Berlin,-250.00
2025-01-18,Train ticket Berlin-Hamburg client visit,-89.00
2025-01-22,Apple MacBook Pro M4 (business equipment),-2899.00
2025-01-25,US client invoice INV-2025-003 paid (Acme Inc),+5800.00
2025-01-31,Steuerberater Schmidt — accounting fees Q4 2024,-450.00
"""


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
            "You are a German tax bookkeeping assistant. When asked to "
            "classify transactions, FIRST call get_skill('germany-vat-return') "
            "and get_skill('vat-workflow-base'), then apply the rules to each "
            "transaction. Output a markdown table with: Date | Description | "
            "Amount | Category (German chart of accounts SKR03/SKR04) | VAT "
            "treatment (19% / 7% / reverse charge / out of scope) | Schedule C "
            "deductible (yes/no/partial). Surface any AUDIT FLASH POINT markers "
            "from the loaded skills."
        ),
    )

    prompt = (
        f"I'm a German Freiberufler under Regelbesteuerung (standard VAT). "
        f"Classify these transactions for my January 2025 VAT return and "
        f"income tax bookkeeping:\n\n{TRANSACTIONS}"
    )
    print(f"User: {prompt}\n")

    response = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    print("Agent:")
    print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
