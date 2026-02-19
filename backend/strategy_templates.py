# ABOUTME: Shared strategy template definitions for wizard UI and conversational agent
# ABOUTME: Single source of truth for filter templates, defaults, and strategy presets

FILTER_TEMPLATES = {
    "warren_buffett_classic": {
        "name": "Warren Buffett Solo",
        "description": "Wonderful businesses at fair prices",
        "use_case": "Find large established companies with strong moats and pricing power",
        "filters": [
            { "field": "roe", "value": 15, "operator": ">=" }, 
            { "field": "pe_ratio", "value": 25, "operator": "<=" }, 
            { "field": "gross_margin", "value": 40, "operator": ">=" }, 
            { "field": "debt_to_earnings", "value": 3, "operator": "<=" }
        ],
        "analysts": ["buffett"], 
        "require_thesis": True, 
        "scoring_requirements": [
            { "character": "buffett", "min_score": 70 }
        ], 
        "thesis_verdict_required": ["BUY"], 
        "addition_scoring_requirements": [
            { "character": "buffett", "min_score": 80 }
        ],
        "position_sizing": {
            "method":"conviction_weighted",
            "max_positions":10,
            "kelly_fraction":None,
            "max_position_pct":50,
            "fixed_position_pct":None,
            "min_position_value":500
        },
        "exit_rules": {
            "max_hold_days":None,
            "stop_loss_pct":None,
            "profit_target_pct":None,
            "score_degradation":{"lynch_below":"","buffett_below":""}
        }
    },
    "peter_lynch_classic": {
        "name": "Peter Lynch Solo",
        "description": "Growth at a reasonable price",
        "use_case": "Find fast growing companies at reasonable valuations",
        "filters": [
            { "field": "peg_ratio", "value": 1.5, "operator": "<=" },
            { "field": "debt_to_equity", "value": 1, "operator": "<=" },
            { "field": "institutional_ownership", "value": 60, "operator": "<=" },
            { "field": "revenue_growth", "value": 12, "operator": ">" },
            { "field": "revenue_growth", "value": 30, "operator": "<=" }
        ],
        "analysts": [
            "lynch"
        ],
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "lynch", "min_score": 70 }
        ],
        "thesis_verdict_required": [ "BUY" ],
        "addition_scoring_requirements": [ { "character": "lynch", "min_score": 80 } ],
        "position_sizing": {
            "method":"conviction_weighted",
            "max_positions":10,
            "kelly_fraction":None,
            "max_position_pct":50,
            "fixed_position_pct":None,
            "min_position_value":500
        },
        "exit_rules": {
            "max_hold_days":None,
            "stop_loss_pct":None,
            "profit_target_pct":None,
            "score_degradation":{"lynch_below":"","buffett_below":""}
        }
    },
    "lynch_buffett_pair": {
        "name": "Lynch and Buffett Team Up",
        "description": "Lynch and Buffett collaborate to find investments they both like",
        "use_case": "Find great investments that both Lynch and Buffet would approve of",
        "filters": [
            { "field": "peg_ratio", "value": 1.5, "operator": "<=" },
            { "field": "debt_to_equity", "value": 1, "operator": "<=" },
            { "field": "institutional_ownership", "value": 60, "operator": "<=" },
            { "field": "revenue_growth", "value": 12, "operator": ">" },
            { "field": "revenue_growth", "value": 30, "operator": "<=" }
        ],
        "analysts": [
            "lynch",
            "buffett"
        ],
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "lynch", "min_score": 70 },
            { "character": "buffett", "min_score": 70 }
        ],
        "thesis_verdict_required": [ "BUY" ],
        "addition_scoring_requirements": [
            { "character": "lynch", "min_score": 80 },
            { "character": "buffett", "min_score": 80 }
        ],
        "position_sizing": {
            "method":"conviction_weighted",
            "max_positions":10,
            "kelly_fraction":None,
            "max_position_pct":50,
            "fixed_position_pct":None,
            "min_position_value":500
        },
        "exit_rules": {
            "max_hold_days":None,
            "stop_loss_pct":None,
            "profit_target_pct":None,
            "score_degradation":{"lynch_below":"","buffett_below":""}
        }
    },
    "beaten_down_large_caps": {
        "name": "Beaten Down Large Caps",
        "description": "Large companies down 20%+ from their 52-week highs. Contrarian value investing.",
        "use_case": "Find large established companies that have been unfairly beaten down",
        "filters": [
            {"field": "price_vs_52wk_high", "operator": "<=", "value": -20},
            {"field": "market_cap", "operator": ">=", "value": 10000000000}
        ]
    },
    "value_stocks": {
        "name": "Value Stocks",
        "description": "Value stocks with low P/E and PEG ratios. Favors mature, profitable companies.",
        "use_case": "Value investing approach",
        "filters": [
            {"field": "pe_ratio", "operator": "<=", "value": 15},
            {"field": "peg_ratio", "operator": "<=", "value": 1.0}
        ]
    },
    "growth_at_reasonable_price": {
        "name": "GARP",
        "description": "Peter Lynch's signature approach. Growth stocks at reasonable prices.",
        "use_case": "Growth stocks at reasonable valuations",
        "filters": [
            {"field": "peg_ratio", "operator": "<=", "value": 1.5},
            {"field": "pe_ratio", "operator": ">=", "value": 5},
            {"field": "pe_ratio", "operator": "<=", "value": 30}
        ]
    },
    "low_debt_stable": {
        "name": "Stable Companies with Low Debt",
        "description": "Conservative strategy to weather economic downturns.",
        "use_case": "Conservative investing with lower risk",
        "filters": [
            {"field": "debt_to_equity", "operator": "<=", "value": 0.5},
            {"field": "market_cap", "operator": ">=", "value": 2000000000}
        ]
    },
    "small_cap_growth": {
        "name": "Small Cap Growth",
        "description": "Small, fast-growing companies. Higher risk, higher potential reward.",
        "use_case": "Higher risk/reward with smaller companies",
        "filters": [
            {"field": "market_cap", "operator": "<=", "value": 3000000000},
            {"field": "market_cap", "operator": ">=", "value": 1000000000},
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
    "require_thesis": True,
    "scoring_requirements": [
        {"character": "lynch", "min_score": 60},
        {"character": "buffett", "min_score": 60}
    ],
    "thesis_verdict_required": ["BUY"],
    "exit_conditions": {
        "stop_loss_pct": -15.0,
        "take_profit_pct": 40.0
    },
    "position_sizing": {
        "method": "conviction_weighted",
        "max_position_pct": 10.0,
        "max_positions": 20
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
    "warren_buffett_classic": {
        "name": "Warren Buffett Solo",
        "description": "Find large established companies with strong moats and pricing power",
        "conditions": {
            "filters": FILTER_TEMPLATES["warren_buffett_classic"]["filters"],
            "analysts": FILTER_TEMPLATES["warren_buffett_classic"]["analysts"],
            "require_thesis": FILTER_TEMPLATES["warren_buffett_classic"]["require_thesis"],
            "scoring_requirements": FILTER_TEMPLATES["warren_buffett_classic"]["scoring_requirements"],
            "thesis_verdict_required": FILTER_TEMPLATES["warren_buffett_classic"]["thesis_verdict_required"],
            "addition_scoring_requirements": FILTER_TEMPLATES["warren_buffett_classic"].get("addition_scoring_requirements")
        },
        "consensus_mode": "either_approves",
        "consensus_threshold": 70.0,
        "position_sizing": FILTER_TEMPLATES["warren_buffett_classic"]["position_sizing"],
        "exit_conditions": {
            "stop_loss_pct": FILTER_TEMPLATES["warren_buffett_classic"]["exit_rules"]["stop_loss_pct"],
            "take_profit_pct": FILTER_TEMPLATES["warren_buffett_classic"]["exit_rules"]["profit_target_pct"]
        },
        "schedule_cron": STRATEGY_DEFAULTS["schedule_cron"],
        "initial_cash": STRATEGY_DEFAULTS["initial_cash"]
    },
    "peter_lynch_classic": {
        "name": "Peter Lynch Solo",
        "description": "Find fast growing companies at reasonable valuations",
        "conditions": {
            "filters": FILTER_TEMPLATES["peter_lynch_classic"]["filters"],
            "analysts": FILTER_TEMPLATES["peter_lynch_classic"]["analysts"],
            "require_thesis": FILTER_TEMPLATES["peter_lynch_classic"]["require_thesis"],
            "scoring_requirements": FILTER_TEMPLATES["peter_lynch_classic"]["scoring_requirements"],
            "thesis_verdict_required": FILTER_TEMPLATES["peter_lynch_classic"]["thesis_verdict_required"],
            "addition_scoring_requirements": FILTER_TEMPLATES["peter_lynch_classic"].get("addition_scoring_requirements")
        },
        "consensus_mode": "either_approves",
        "consensus_threshold": 70.0,
        "position_sizing": FILTER_TEMPLATES["peter_lynch_classic"]["position_sizing"],
        "exit_conditions": {
            "stop_loss_pct": FILTER_TEMPLATES["peter_lynch_classic"]["exit_rules"]["stop_loss_pct"],
            "take_profit_pct": FILTER_TEMPLATES["peter_lynch_classic"]["exit_rules"]["profit_target_pct"]
        },
        "schedule_cron": STRATEGY_DEFAULTS["schedule_cron"],
        "initial_cash": STRATEGY_DEFAULTS["initial_cash"]
    },
    "lynch_buffett_pair": {
        "name": "Lynch and Buffett Team Up",
        "description": "Find great investments that both Lynch and Buffet would approve of",
        "conditions": {
            "filters": FILTER_TEMPLATES["lynch_buffett_pair"]["filters"],
            "analysts": FILTER_TEMPLATES["lynch_buffett_pair"]["analysts"],
            "require_thesis": FILTER_TEMPLATES["lynch_buffett_pair"]["require_thesis"],
            "scoring_requirements": FILTER_TEMPLATES["lynch_buffett_pair"]["scoring_requirements"],
            "thesis_verdict_required": FILTER_TEMPLATES["lynch_buffett_pair"]["thesis_verdict_required"],
            "addition_scoring_requirements": FILTER_TEMPLATES["lynch_buffett_pair"].get("addition_scoring_requirements")
        },
        "consensus_mode": "both_agree",
        "consensus_threshold": 70.0,
        "position_sizing": FILTER_TEMPLATES["lynch_buffett_pair"]["position_sizing"],
        "exit_conditions": {
            "stop_loss_pct": FILTER_TEMPLATES["lynch_buffett_pair"]["exit_rules"]["stop_loss_pct"],
            "take_profit_pct": FILTER_TEMPLATES["lynch_buffett_pair"]["exit_rules"]["profit_target_pct"]
        },
        "schedule_cron": STRATEGY_DEFAULTS["schedule_cron"],
        "initial_cash": STRATEGY_DEFAULTS["initial_cash"]
    }
}
