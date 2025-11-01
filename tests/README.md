# Tests for APA Citation Checker

This directory contains all unit tests for the APA Citation Checker application.

## Running Tests

### Run individual tests:
```bash
# From the tests directory
cd tests
python test_citation_detection.py
python test_full_matching.py
python test_fuzzy_matching.py
# ... etc

# Or from the project root
python tests/test_citation_detection.py
python tests/test_full_matching.py
# ... etc
```

### Run all tests:
```bash
# From the project root
python -m pytest tests/
```

## Test Files

- `test_citation_detection.py` - End-to-end test for citation detection and matching
- `test_full_matching.py` - Tests complete matching with correct Aly & Kojima and Hillman formats
- `test_fuzzy_matching.py` - Tests author and year extraction functionality
- `test_two_author_extraction.py` - Tests two-author citation extraction
- `test_kojima_suggestion.py` - Tests suggestion feature for incomplete author citations
- `test_compound_names.py` - Tests compound surname handling (De Menezes, Van der Berg, etc.)
- `test_reference_parsing.py` - Tests reference section parsing
- `test_extraction.py` - Tests citation extraction from text
- `test_matching.py` - Tests citation-reference matching logic
- `test_two_authors.py` - Tests two-author reference parsing

## Notes

- All test files have been configured to work from the `tests/` directory
- Import paths are automatically adjusted using `sys.path.insert()`
- Tests can be run individually or as a suite
