"""
OUTPUT FORMATTER - Format JSON/text to readable
"""

import json


class OutputFormatter:
    """Format output to readable markdown."""

    @staticmethod
    def json_to_table(data_str):
        try:
            data = json.loads(data_str)
        except:
            return data_str

        if isinstance(data, dict):
            rows = []
            for k, v in data.items():
                rows.append(f"| {k} | {v} |")
            header = "| Key | Value |\n|---|---|\n"
            return header + "\n".join(rows)

        if isinstance(data, list) and data and isinstance(data[0], dict):
            headers = list(data[0].keys())
            header_row = "| " + " | ".join(headers) + " |"
            sep_row = "| " + " | ".join(["---"] * len(headers)) + " |"
            table_rows = [header_row, sep_row]
            for item in data[:10]:
                row = "| " + " | ".join(str(item.get(h, "") for h in headers)
                table_rows.append(row)
            return "\n".join(table_rows)

        return data_str

    @staticmethod
    def format(text, fmt="auto"):
        if fmt == "auto":
            fmt = "table" if text.strip().startswith("[") or text.strip().startswith("{") else "tree"
        if fmt == "table":
            return OutputFormatter.json_to_table(text)
        return text
