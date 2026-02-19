# ABOUTME: Shared strategy template definitions for wizard UI and conversational agent
# ABOUTME: Single source of truth for filter templates, defaults, and strategy presets

"""
Examples of country or region filters:
        "filters": [
            # Multi-country support example:
            { "field": "country", "value": ["US", "CA", "GB", "DE"], "operator": "in" },
            # Region support example (North America includes US, CA, MX):
            { "field": "region", "value": "North America", "operator": "==" }

        ],

"""
FILTER_TEMPLATES = {
    "warren_buffett_classic": {
        "name": "Warren Buffett Solo",
        "description": "Wonderful businesses at fair prices",
        "use_case": "Find large established US companies with strong moats and pricing power. Buffett evaluates alone.",
        "filters": [
            { "field": "market_cap", "value": 2000000000, "operator": ">=" }, # > $2B
            { "field": "country", "value": "US", "operator": "==" }
        ],
        "analysts": ["buffett"],
        "consensus_mode": "both_agree",
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "buffett", "min_score": 70 }
        ],
        "thesis_verdict_required": ["BUY"],
        "addition_scoring_requirements": [
            { "character": "buffett", "min_score": 80 }
        ],
        "position_sizing": {
            "method": "conviction_weighted",
            "max_positions": 10,
            "kelly_fraction": None,
            "max_position_pct": 20,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": None,
            "profit_target_pct": None,
            "score_degradation": {"lynch_below": "", "buffett_below": ""}
        }
    },
    "peter_lynch_classic": {
        "name": "Peter Lynch Solo",
        "description": "Growth at a reasonable price",
        "use_case": "Find fast-growing companies at reasonable valuations across English-speaking markets. Lynch evaluates alone.",
        "filters": [
            { "field": "market_cap", "value": 100000000, "operator": ">=" }, # > $100M
            { "field": "country", "value": ["US", "CA", "GB", "DE"], "operator": "in" }
        ],
        "analysts": ["lynch"],
        "consensus_mode": "both_agree",
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "lynch", "min_score": 70 }
        ],
        "thesis_verdict_required": ["BUY"],
        "addition_scoring_requirements": [
            { "character": "lynch", "min_score": 80 }
        ],
        "position_sizing": {
            "method": "conviction_weighted",
            "max_positions": 15,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": None,
            "profit_target_pct": None,
            "score_degradation": {"lynch_below": "", "buffett_below": ""}
        }
    },
    "lynch_buffett_pair": {
        "name": "Lynch & Buffett Team Up",
        "description": "Lynch and Buffett collaborate on every investment decision",
        "use_case": "Find great investments that both Lynch and Buffett approve of. Requires high agreement — fewer but higher-conviction picks.",
        "filters": [
            { "field": "market_cap", "value": 1000000000, "operator": ">=" }, # > $1B
            { "field": "country", "value": ["US", "CA", "GB", "DE"], "operator": "in" }
        ],
        "analysts": ["lynch", "buffett"],
        "consensus_mode": "both_agree",
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "lynch", "min_score": 70 },
            { "character": "buffett", "min_score": 70 }
        ],
        "thesis_verdict_required": ["BUY"],
        "addition_scoring_requirements": [
            { "character": "lynch", "min_score": 80 },
            { "character": "buffett", "min_score": 80 }
        ],
        "position_sizing": {
            "method": "conviction_weighted",
            "max_positions": 10,
            "kelly_fraction": None,
            "max_position_pct": 20,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": None,
            "profit_target_pct": None,
            "score_degradation": {"lynch_below": "", "buffett_below": ""}
        }
    },
    "small_cap_growth": {
        "name": "Small Cap Growth",
        "description": "Small, fast-growing companies. Higher risk, higher potential reward.",
        "use_case": "Lynch scours the small-cap universe ($300M–$3B) for hidden gems with strong growth. Either analyst approval is enough to invest.",
        "filters": [
            { "field": "market_cap", "operator": ">=", "value": 300000000 },   # > $300M
            { "field": "market_cap", "operator": "<=", "value": 3000000000 },  # < $3B
            { "field": "country", "value": ["US", "CA"], "operator": "in" }
        ],
        "analysts": ["lynch"],
        "consensus_mode": "both_agree",
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "lynch", "min_score": 65 }
        ],
        "thesis_verdict_required": ["BUY"],
        "addition_scoring_requirements": [
            { "character": "lynch", "min_score": 75 }
        ],
        "position_sizing": {
            "method": "equal_weight",
            "max_positions": 20,
            "kelly_fraction": None,
            "max_position_pct": 10,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": None,
            "score_degradation": {"lynch_below": "", "buffett_below": ""}
        }
    },
    "global_growth": {
        "name": "Global Growth",
        "description": "Lynch and Buffett hunt for the world's best businesses with no geographic constraints",
        "use_case": "Diversified globally across developed markets. Both analysts deliberate. Best for investors comfortable with international exposure.",
        "filters": [
            { "field": "market_cap", "value": 500000000, "operator": ">=" }
            # No country filter — global universe
        ],
        "analysts": ["lynch", "buffett"],
        "consensus_mode": "weighted_confidence",
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "lynch", "min_score": 65 },
            { "character": "buffett", "min_score": 65 }
        ],
        "thesis_verdict_required": ["BUY"],
        "addition_scoring_requirements": [
            { "character": "lynch", "min_score": 75 },
            { "character": "buffett", "min_score": 75 }
        ],
        "position_sizing": {
            "method": "conviction_weighted",
            "max_positions": 20,
            "kelly_fraction": None,
            "max_position_pct": 12,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": None,
            "profit_target_pct": None,
            "score_degradation": {"lynch_below": "", "buffett_below": ""}
        }
    },
    "dividend_value": {
        "name": "Dividend Income",
        "description": "Large, profitable companies that reward shareholders with dividends",
        "use_case": "Buffett focuses on large-cap US companies known for stable cash flows and consistent dividends. Concentrated, low-turnover portfolio.",
        "filters": [
            { "field": "market_cap", "operator": ">=", "value": 5000000000 },  # > $5B
            { "field": "country", "value": "US", "operator": "==" }
        ],
        "analysts": ["buffett"],
        "consensus_mode": "both_agree",
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "buffett", "min_score": 72 }
        ],
        "thesis_verdict_required": ["BUY"],
        "addition_scoring_requirements": [
            { "character": "buffett", "min_score": 82 }
        ],
        "position_sizing": {
            "method": "conviction_weighted",
            "max_positions": 8,
            "kelly_fraction": None,
            "max_position_pct": 25,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": None,
            "profit_target_pct": None,
            "score_degradation": {"lynch_below": "", "buffett_below": ""}
        }
    },
    "beaten_down_contrarian": {
        "name": "Beaten-Down Contrarian",
        "description": "Large companies down 20%+ from their 52-week highs. Contrarian value investing.",
        "use_case": "Buffett looks for quality large-caps unfairly punished by the market. Requires high conviction before buying into weakness.",
        "filters": [
            { "field": "price_vs_52wk_high", "operator": "<=", "value": -20 },
            { "field": "market_cap", "operator": ">=", "value": 5000000000 },  # > $5B
            { "field": "country", "value": ["US", "CA", "GB"], "operator": "in" }
        ],
        "analysts": ["buffett"],
        "consensus_mode": "both_agree",
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "buffett", "min_score": 75 }
        ],
        "thesis_verdict_required": ["BUY"],
        "addition_scoring_requirements": [
            { "character": "buffett", "min_score": 85 }
        ],
        "position_sizing": {
            "method": "conviction_weighted",
            "max_positions": 8,
            "kelly_fraction": None,
            "max_position_pct": 20,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -15,
            "profit_target_pct": None,
            "score_degradation": {"lynch_below": "", "buffett_below": ""}
        }
    },
    "conservative_quality": {
        "name": "Conservative Quality",
        "description": "A disciplined, low-concentration portfolio of only the highest-conviction US names",
        "use_case": "Lynch and Buffett must both strongly agree. Very selective — only the strongest ideas make it in. Designed for capital preservation with growth.",
        "filters": [
            { "field": "market_cap", "value": 10000000000, "operator": ">=" }, # > $10B
            { "field": "country", "value": "US", "operator": "==" }
        ],
        "analysts": ["lynch", "buffett"],
        "consensus_mode": "both_agree",
        "require_thesis": True,
        "scoring_requirements": [
            { "character": "lynch", "min_score": 75 },
            { "character": "buffett", "min_score": 75 }
        ],
        "thesis_verdict_required": ["BUY"],
        "addition_scoring_requirements": [
            { "character": "lynch", "min_score": 85 },
            { "character": "buffett", "min_score": 85 }
        ],
        "position_sizing": {
            "method": "conviction_weighted",
            "max_positions": 6,
            "kelly_fraction": None,
            "max_position_pct": 30,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": None,
            "profit_target_pct": None,
            "score_degradation": {"lynch_below": "", "buffett_below": ""}
        }
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
    "lynch": ["peter_lynch_classic", "small_cap_growth", "global_growth"],
    "buffett": ["warren_buffett_classic", "dividend_value", "beaten_down_contrarian", "conservative_quality"]
}


def _make_quick_start(key):
    """Build a QUICK_START_CONFIGS entry from a FILTER_TEMPLATES entry."""
    t = FILTER_TEMPLATES[key]
    stop_loss = t["exit_rules"].get("stop_loss_pct")
    profit_target = t["exit_rules"].get("profit_target_pct")
    return {
        "name": t["name"],
        "description": t["use_case"],
        "conditions": {
            "filters": t["filters"],
            "analysts": t["analysts"],
            "require_thesis": t["require_thesis"],
            "scoring_requirements": t["scoring_requirements"],
            "thesis_verdict_required": t["thesis_verdict_required"],
            "addition_scoring_requirements": t.get("addition_scoring_requirements"),
        },
        "consensus_mode": t.get("consensus_mode", "both_agree"),
        "consensus_threshold": 70.0,
        "position_sizing": t["position_sizing"],
        "exit_conditions": {
            "stop_loss_pct": stop_loss,
            "take_profit_pct": profit_target
        },
        "schedule_cron": STRATEGY_DEFAULTS["schedule_cron"],
        "initial_cash": STRATEGY_DEFAULTS["initial_cash"]
    }


# Complete ready-to-run configs for quick-start onboarding.
# Each bundles a filter template with scoring, position sizing, and exit defaults.
QUICK_START_CONFIGS = {key: _make_quick_start(key) for key in FILTER_TEMPLATES}
