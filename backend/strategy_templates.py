# ABOUTME: Shared strategy template definitions for wizard UI and conversational agent
# ABOUTME: Single source of truth for filter templates, defaults, and strategy presets

FILTER_TEMPLATES = {
    "beaten_down_large_caps": {
        "name": "Beaten Down Large Caps",
        "description": "Large cap companies down 20%+ from their 52-week highs. Good for contrarian value investing.",
        "use_case": "Find large established companies that have been unfairly beaten down",
        "filters": [
            {"field": "price_vs_52wk_high", "operator": "<=", "value": -20},
            {"field": "market_cap", "operator": ">=", "value": 10000000000}
        ]
    },
    "value_stocks": {
        "name": "Value Stocks",
        "description": "Traditional value stocks with low P/E and PEG ratios. Favors mature, profitable companies.",
        "use_case": "Traditional value investing approach",
        "filters": [
            {"field": "pe_ratio", "operator": "<=", "value": 15},
            {"field": "peg_ratio", "operator": "<=", "value": 1.0}
        ]
    },
    "growth_at_reasonable_price": {
        "name": "Growth at Reasonable Price (GARP)",
        "description": "GARP strategy: PEG < 1.5 indicates growth trading below its rate. Peter Lynch's preferred approach.",
        "use_case": "Growth stocks at reasonable valuations",
        "filters": [
            {"field": "peg_ratio", "operator": "<=", "value": 1.5},
            {"field": "pe_ratio", "operator": ">=", "value": 5},
            {"field": "pe_ratio", "operator": "<=", "value": 30}
        ]
    },
    "low_debt_stable": {
        "name": "Low Debt, Stable Companies",
        "description": "Conservative companies with low leverage. Safer during economic downturns.",
        "use_case": "Conservative investing with lower risk",
        "filters": [
            {"field": "debt_to_equity", "operator": "<=", "value": 0.5},
            {"field": "market_cap", "operator": ">=", "value": 2000000000}
        ]
    },
    "small_cap_growth": {
        "name": "Small Cap Growth",
        "description": "Small cap companies ($300M-$2B) with growth characteristics. Higher risk, higher potential reward.",
        "use_case": "Higher risk/reward with smaller companies",
        "filters": [
            {"field": "market_cap", "operator": ">=", "value": 300000000},
            {"field": "market_cap", "operator": "<=", "value": 2000000000},
            {"field": "pe_ratio", "operator": ">=", "value": 10},
            {"field": "pe_ratio", "operator": "<=", "value": 40}
        ]
    },
    "dividend_value": {
        "name": "Dividend Value Plays",
        "description": "Value-oriented companies likely to pay dividends. Low P/E, larger market caps.",
        "use_case": "Income-focused value investing",
        "filters": [
            {"field": "pe_ratio", "operator": "<=", "value": 15},
            {"field": "market_cap", "operator": ">=", "value": 5000000000},
            {"field": "debt_to_equity", "operator": "<=", "value": 1.0}
        ]
    }
}

STRATEGY_DEFAULTS = {
    "position_sizing": {
        "method": "equal_weight",
        "max_position_pct": 10.0,
        "max_positions": 50
    },
    "consensus_mode": "both_agree",
    "consensus_threshold": 70.0,
    "schedule_cron": "0 9 * * 1-5",
    "initial_cash": 100000.0
}

# Character-specific template recommendations
# Used by personas to suggest appropriate strategies
CHARACTER_RECOMMENDATIONS = {
    "lynch": ["growth_at_reasonable_price", "small_cap_growth"],
    "buffett": ["low_debt_stable", "value_stocks", "dividend_value"]
}

# Complete ready-to-run configs for quick-start onboarding.
# Each bundles a filter template with scoring, position sizing, and exit defaults.
QUICK_START_CONFIGS = {
    "beaten_down_large_caps": {
        "name": "Beaten Down Large Caps",
        "description": "Contrarian strategy targeting large caps down 20%+ from highs",
        "conditions": {"filters": FILTER_TEMPLATES["beaten_down_large_caps"]["filters"]},
        "consensus_mode": "either_approves",
        "consensus_threshold": 65.0,
        "position_sizing": {
            "method": "equal_weight",
            "max_position_pct": 8.0,
            "max_positions": 15
        },
        "exit_conditions": {
            "stop_loss_pct": -15.0,
            "take_profit_pct": 40.0
        },
        "schedule_cron": "0 14 * * 1-5",
        "initial_cash": 100000.0
    },
    "value_stocks": {
        "name": "Value Stocks",
        "description": "Traditional value investing with low P/E and PEG ratios",
        "conditions": {"filters": FILTER_TEMPLATES["value_stocks"]["filters"]},
        "consensus_mode": "both_agree",
        "consensus_threshold": 70.0,
        "position_sizing": {
            "method": "equal_weight",
            "max_position_pct": 8.0,
            "max_positions": 20
        },
        "exit_conditions": {
            "stop_loss_pct": -12.0,
            "take_profit_pct": 30.0
        },
        "schedule_cron": "0 14 * * 1-5",
        "initial_cash": 100000.0
    },
    "growth_at_reasonable_price": {
        "name": "Growth at Reasonable Price",
        "description": "Peter Lynch's GARP approach — growth stocks at fair valuations",
        "conditions": {"filters": FILTER_TEMPLATES["growth_at_reasonable_price"]["filters"]},
        "consensus_mode": "both_agree",
        "consensus_threshold": 70.0,
        "position_sizing": {
            "method": "equal_weight",
            "max_position_pct": 7.0,
            "max_positions": 20
        },
        "exit_conditions": {
            "stop_loss_pct": -15.0,
            "take_profit_pct": 50.0
        },
        "schedule_cron": "0 14 * * 1-5",
        "initial_cash": 100000.0
    },
    "low_debt_stable": {
        "name": "Low Debt, Stable Companies",
        "description": "Conservative picks with low leverage — safer during downturns",
        "conditions": {"filters": FILTER_TEMPLATES["low_debt_stable"]["filters"]},
        "consensus_mode": "both_agree",
        "consensus_threshold": 75.0,
        "position_sizing": {
            "method": "equal_weight",
            "max_position_pct": 6.0,
            "max_positions": 25
        },
        "exit_conditions": {
            "stop_loss_pct": -10.0,
            "take_profit_pct": 25.0
        },
        "schedule_cron": "0 14 * * 1-5",
        "initial_cash": 100000.0
    },
    "small_cap_growth": {
        "name": "Small Cap Growth",
        "description": "Higher risk/reward with $300M-$2B market cap growth stocks",
        "conditions": {"filters": FILTER_TEMPLATES["small_cap_growth"]["filters"]},
        "consensus_mode": "either_approves",
        "consensus_threshold": 65.0,
        "position_sizing": {
            "method": "equal_weight",
            "max_position_pct": 5.0,
            "max_positions": 25
        },
        "exit_conditions": {
            "stop_loss_pct": -20.0,
            "take_profit_pct": 60.0
        },
        "schedule_cron": "0 14 * * 1-5",
        "initial_cash": 100000.0
    },
    "dividend_value": {
        "name": "Dividend Value Plays",
        "description": "Income-focused value investing with larger, stable companies",
        "conditions": {"filters": FILTER_TEMPLATES["dividend_value"]["filters"]},
        "consensus_mode": "both_agree",
        "consensus_threshold": 70.0,
        "position_sizing": {
            "method": "equal_weight",
            "max_position_pct": 7.0,
            "max_positions": 20
        },
        "exit_conditions": {
            "stop_loss_pct": -10.0,
            "take_profit_pct": 30.0
        },
        "schedule_cron": "0 14 * * 1-5",
        "initial_cash": 100000.0
    }
}
