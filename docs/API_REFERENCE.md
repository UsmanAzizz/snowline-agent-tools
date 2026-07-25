# API Reference

## SnowlineCompanion

Main class untuk semua operations.

### Methods

#### `handle_request(agent_request: Dict) -> Dict`

Process tool request dari agent. Akan divalidasi dan dikembalikan dengan guidance.

**Parameters:**
- `agent_request`: `{ "tool": "tool_name", "params": {...} }`

**Returns:** Structured response dengan guidance & result preview (dry-run).

#### `execute(agent_request: Dict) -> Dict`

Execute tool sungguhan (hanya jika agen sudah mengerti risikonya dan mengirim dry_run=False).

## OpenAIAdapter

Bridge ke OpenAI function calling.

### Methods

#### `handle_tool_call(tool_name: str, arguments: Dict) -> Dict`

Process tool call dari LLM. Ini membungkus fungsi `handle_request` dari `SnowlineCompanion`.

#### `build_system_prompt() -> str`

Get system prompt yang enforce Snowline protocol agar dipatuhi oleh agent.

#### `tools_schema -> List[Dict]`

Property yang me-return skema tool lengkap (parameters, description) dalam format fungsi OpenAI.
