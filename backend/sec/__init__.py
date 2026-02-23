# ABOUTME: Package entry point for SEC data fetching and rate limiting.
# ABOUTME: Re-exports public API classes and functions.

# Eagerly import lightweight modules (no circular dependency risk)
from sec.sec_rate_limiter import SEC_RATE_LIMITER, configure_edgartools_rate_limit
from sec.sec_rss_client import SECRSSClient

# Lazy imports to avoid circular dependency:
# sec_data_fetcher → edgar_fetcher → sec (cycle)
# sec_8k_client → edgar (edgartools, heavy)


def __getattr__(name):
    if name == "SECDataFetcher":
        from sec.sec_data_fetcher import SECDataFetcher
        return SECDataFetcher
    if name == "SEC8KClient":
        from sec.sec_8k_client import SEC8KClient
        return SEC8KClient
    if name == "SECPostgresMigrator":
        from sec.migrate_sec_to_postgres import SECPostgresMigrator
        return SECPostgresMigrator
    raise AttributeError(f"module 'sec' has no attribute {name!r}")
