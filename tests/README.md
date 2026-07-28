# Tests for Snowline Agent Tools

This folder contains tests for the tools.

## Structure

```
tests/
├── test_tree_gen.py      # Tests for shared tree module
├── test_scope_guardian.py # Tests for scope guardian
└── mocks/               # Mock files for testing
    ├── sample.js
    ├── sample.py
    └── project/
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_tree_gen.py

# Run with coverage
pytest tests/ --cov
```

## Test Categories

1. **Unit Tests** - Test individual functions in isolation
2. **Integration Tests** - Test tools end-to-end
3. **Mock Tests** - Test with fake project structures
