import json
import copy

class BaseAdapter:
    def format_payload(self, golden_payload_dict: dict) -> dict:
        raise NotImplementedError

class AnthropicAdapter(BaseAdapter):
    def format_payload(self, golden_payload_dict: dict) -> dict:
        payload = copy.deepcopy(golden_payload_dict)
        if "system" in payload and isinstance(payload["system"], list) and len(payload["system"]) > 0:
            # Inject cache_control to the last block of the system prompt array
            payload["system"][-1]["cache_control"] = {"type": "ephemeral"}
        return payload

class GeminiAdapter(BaseAdapter):
    def format_payload(self, golden_payload_dict: dict) -> dict:
        payload = copy.deepcopy(golden_payload_dict)
        # Translate into a different form (simulate gemini model standard, changing system to system_instruction)
        if "system" in payload:
            payload["system_instruction"] = payload.pop("system")
        return payload

class AdapterFactory:
    @staticmethod
    def get_adapter(adapter_name: str) -> BaseAdapter:
        name = adapter_name.lower()
        if name == "anthropic":
            return AnthropicAdapter()
        elif name == "gemini":
            return GeminiAdapter()
        else:
            raise ValueError(f"Unknown adapter: {adapter_name}")

if __name__ == '__main__':
    # Define a golden payload dict
    golden_payload = {
        "system": [
            {"type": "text", "text": "You are a helpful assistant."},
            {"type": "text", "text": "Ensure your answers are concise and accurate."}
        ],
        "messages": [
            {"role": "user", "content": "Can you summarize the meeting notes?"}
        ],
        "temperature": 0.7
    }

    print("=== Original Golden Payload ===")
    print(json.dumps(golden_payload, indent=2))
    print("\n")

    # Anthropic Adapter Test
    anthropic_adapter = AdapterFactory.get_adapter("anthropic")
    anthropic_payload = anthropic_adapter.format_payload(golden_payload)
    print("=== Anthropic Adapter Output ===")
    print(json.dumps(anthropic_payload, indent=2))
    print("\n")

    # Gemini Adapter Test
    gemini_adapter = AdapterFactory.get_adapter("gemini")
    gemini_payload = gemini_adapter.format_payload(golden_payload)
    print("=== Gemini Adapter Output ===")
    print(json.dumps(gemini_payload, indent=2))
    print("\n")
