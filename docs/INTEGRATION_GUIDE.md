# Integration Guide

## Step 1: Initialize Snowline

```python
from snowline import SnowlineCompanion
from snowline.adapters import OpenAIAdapter

companion = SnowlineCompanion(config_path="snowline.yaml")
adapter = OpenAIAdapter(companion, api_key="YOUR_API_KEY")
```

## Step 2: Get System Prompt & Tools Schema

```python
system_prompt = adapter.build_system_prompt()
tools_schema = adapter.tools_schema
```

## Step 3: Use with Claude/GPT

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=system_prompt,
    tools=tools_schema,
    messages=[
        {"role": "user", "content": "Replace 'foo' with 'bar'"}
    ]
)
```

## Step 4: Handle Tool Calls

```python
for block in response.content:
    if block.type == "tool_use":
        result = adapter.handle_tool_call(block.name, block.input)
        # Return result to agent, passing Snowline's structured guidance
```

See `example_mock_integration.py` for a complete example of simulated compliance logic.
