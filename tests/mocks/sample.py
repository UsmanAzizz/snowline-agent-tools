# Mock Python file for testing
import os
import sys

class DataProcessor:
    def __init__(self, config):
        self.config = config

    def process(self, data):
        return [self.transform(item) for item in data]

    def transform(self, item):
        return item.upper()

def main():
    processor = DataProcessor({"mode": "test"})
    result = processor.process(["a", "b", "c"])
    print(result)

if __name__ == "__main__":
    main()
