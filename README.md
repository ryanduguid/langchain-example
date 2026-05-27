# LangChain + OpenAccountants

Working examples of using [LangChain](https://github.com/langchain-ai/langchain) with the [OpenAccountants MCP server](https://www.openaccountants.com/api/mcp) — an open library of **800+ accountant-verified tax skills across 190+ jurisdictions**, signed off by named licensed accountants.

## Why

When your LangChain agent needs to compute Malta VAT, classify German bookkeeping transactions, or walk a user through a US Schedule C, **it should call accountant-built skills, not hallucinate**. OpenAccountants is the open library that supplies those skills, every one signed by a named CPA / EA / Steuerberater / Chartered Accountant.

| | Without OpenAccountants | With OpenAccountants |
|---|---|---|
| Tax computation | LLM guess from training data | Skill from the accountant who actually files this regularly |
| Auditability | None — model output is opaque | Every skill has a verifier name + Calendly link + version |
| Jurisdictional coverage | "I think Malta uses…" | 190+ countries / US states with deep packs |
| Updates | Whenever training data refreshes | Annual rates JSON refreshed every December |
| Source code | N/A | [github.com/openaccountants/openaccountants](https://github.com/openaccountants/openaccountants) (AGPL-3.0) |

## Install

```bash
pip install langchain-mcp-adapters langchain-anthropic
```

The MCP server is public — no signup, no API key, just point at the URL.

## Minimal example

```python
import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client = MultiServerMCPClient({
        "openaccountants": {
            "transport": "streamable_http",
            "url": "https://www.openaccountants.com/api/mcp",
        }
    })
    tools = await client.get_tools()
    agent = create_agent("anthropic:claude-sonnet-4-5", tools)

    response = await agent.ainvoke({
        "messages": "I'm a Maltese freelancer earning EUR 45,000 from foreign clients. What VAT obligations do I have?"
    })
    print(response["messages"][-1].content)

asyncio.run(main())
```

The agent calls `start({intent: 'VAT', jurisdiction: 'MT'})` to scope, then `get_skill({slug: 'malta-vat-return'})` to load the rules signed by Michael Cutajar, CPA (Malta), and walks the user through Article 10 vs Article 11, the EUR 35,000 threshold, EU reverse charge, and the Calendly handoff for review.

## What's in this repo

- `examples/01_minimal.py` — Malta VAT walkthrough (above)
- `examples/02_classify_transactions.py` — Classify German bank statement transactions for VAT + bookkeeping
- `examples/03_compare_jurisdictions.py` — Cross-border tax comparison (MT vs IE vs PT for EUR 200k consulting income)
- `notebooks/openaccountants_tax_agent.ipynb` — Interactive notebook version of the minimal example

## The five MCP tools you get

| Tool | Purpose |
|---|---|
| `start` | **Front door.** Pass `intent` (free text, e.g. `"taxes"`, `"VAT return"`, `"set up a company"`) + `jurisdiction` (ISO code) → returns a ready-to-execute plan listing the skills to load. Call this FIRST. |
| `list_skills` | List published skills filtered by jurisdiction / category. |
| `get_skill` | Fetch a single skill's full markdown including the provenance footer (verifier name, Calendly link, audit-flash-point markers). |
| `get_skill_sections` | Same content split into headed sections — useful for very large skills (e.g. NY IT-201). |
| `search_skills` | Keyword search across published skill content. |

All read-only. The server is rate-limited at 60 req/min per IP — generous for honest use, blocks scrapers.

## Jurisdictions

Deep packs exist for: **Malta · UK · Germany · Italy · France · Spain · Portugal · Ireland · Netherlands · US federal + 24 deep state packs (CA, NY, TX, FL, IL, OH, PA, MA, NJ, NC, MI, OR, WA, NH, DE, VA, GA, AZ, CO, NV, MN, MO, MD…) · Canada federal + provincial · India · Indonesia · China (简体中文) · Pakistan · Brazil (PT-BR) · Saudi Arabia · South Africa · Nigeria · Kenya** — plus cross-border matrices (PTE elections, sales-tax nexus, FATCA/FBAR, GILTI/FDII/BEAT, etc.).

Every other UN member state has at least foundational coverage.

## Important — disclaimer

These skills produce **working papers, not filed returns**. Every output preserves a "Talk to a verified accountant" footer with a Calendly link. No client–accountant relationship is created by reading or applying these skills — that requires a formal engagement letter signed by both you and a verified accountant.

## License

This examples repo is **MIT-licensed**. The underlying skill content fetched from the MCP server is **AGPL-3.0 with attribution** per [openaccountants/openaccountants](https://github.com/openaccountants/openaccountants/blob/main/LICENSE-ADDITIONAL.md). Commercial licensing available via `info@openaccountants.com`.

## Links

- **Website**: [openaccountants.com](https://www.openaccountants.com)
- **Skills source** (AGPL): [github.com/openaccountants/openaccountants](https://github.com/openaccountants/openaccountants)
- **MCP server**: `https://www.openaccountants.com/api/mcp`
- **Verified accountant network**: [openaccountants.com/network](https://www.openaccountants.com/network)
- **Book a verified accountant**: [calendly.com/openaccountants-info/30min](https://calendly.com/openaccountants-info/30min)

---

Built with the [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) package.
