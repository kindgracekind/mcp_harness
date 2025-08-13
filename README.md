# mcp harness

Demonstration of using MCP servers to test agents. Companion to [this blog post](https://gracekind.net/blog/mcpblackbox).

## Usage

In one terminal, run the agent:

```bash
uv run -m agents.agent
```

In another terminal, run tests:

```bash
uv run -m tests.math_test
```
