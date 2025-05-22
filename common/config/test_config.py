# common/config/special_chars_test/test_config.py
"""
Configuration for special character testing
"""

# Special symbols to test in input fields
SPECIAL_SYMBOLS = "!@#$%^&*()_+{}:\">?<"

# Domains to test with their document IDs
TEST_DOMAINS = [
    {"domain": "stage15.office.sovasystem.com", "doc_id": 5431},
    {"domain": "stage15.office.sovamaxusa.com", "doc_id": 1},
    {"domain": "stage15.office.ratrading.eu", "doc_id": 1},
    {"domain": "stage15.office.agavasystem.com", "doc_id": 1},
    {"domain": "stage15.office.laniustoys.com", "doc_id": 1},
    {"domain": "stage15.office.dbreactor.com", "doc_id": 1},
    {"domain": "stage15.office.horustrading.eu", "doc_id": 1},
    {"domain": "stage15.office.atlastradingworld.com", "doc_id": 1},
    {"domain": "stage15.office.eminiasystem.com", "doc_id": 5431}
]

# Test user credentials
TEST_USER = {
    "username": "victor.moisei@mteam.md",
    "password": "12"
}

# Timeouts
TIMEOUTS = {
    "login": 10,
    "action": 5,
    "page_load": 15
}