"""Compatibility entry point for the local AWS Bedrock AI workflow.

The former OpenAI tool-calling implementation is retired. Network collection
and deterministic scoring remain local; this module invokes Bedrock only after
the complete local assessment has been produced.
"""

import asyncio

from agent import run_cli


async def main() -> None:
    await run_cli(force_ai=True)


if __name__ == "__main__":
    asyncio.run(main())
