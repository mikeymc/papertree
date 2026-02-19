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
    # ── STRATEGY 1: Buffett's Fortress ──────────────────────────────────────────
    # Buffett solo · US-only · Large-cap ($10B+)
    # Safety-first. Mega-cap US businesses with impenetrable moats.
    "buffett_fortress": {
        "name": "Buffett's Fortress",
        "description": "Impenetrable US blue chips with wide moats",
        "use_case": "Buffett scours the US large-cap universe for indestructible businesses. Concentrated, high-conviction. Optimized for capital preservation with steady compounding.",
        "filters": [
            { "field": "market_cap", "value": 10000000000, "operator": ">=" },  # > $10B
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 2: Lynch's Tenbagger Hunt ──────────────────────────────────────
    # Lynch solo · North America · Any size ($500M+)
    # Pure growth, no ceiling. Lynch finds the $500M company before it becomes $5B.
    "lynch_tenbagger": {
        "name": "Lynch's Tenbagger Hunt",
        "description": "Finding the next 10x before Wall Street notices",
        "use_case": "Lynch combs North America for companies with explosive growth potential at any size. No ceiling — the goal is to find tomorrow's blue chips today.",
        "filters": [
            { "field": "market_cap", "value": 500000000, "operator": ">=" },  # > $500M
            { "field": "region", "value": "North America", "operator": "==" }
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 3: The Dream Team ───────────────────────────────────────────────
    # Lynch + Buffett · North America · All sizes ($300M+)
    # Flagship. Both must agree. Fewer picks but every pick is heavyweight.
    "dream_team": {
        "name": "The Dream Team",
        "description": "Lynch and Buffett must both agree — only the best survive",
        "use_case": "The flagship strategy. Lynch and Buffett deliberate on every pick across North America. High bar, high conviction. Fewer positions, but every one is battle-tested by two legends.",
        "filters": [
            { "field": "market_cap", "value": 300000000, "operator": ">=" },  # > $300M
            { "field": "region", "value": "North America", "operator": "==" }
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 4: Small-Cap Hidden Gems ────────────────────────────────────────
    # Lynch solo · US + Canada · Small-cap ($100M–$3B)
    # High risk, high reward. Lynch in his natural habitat.
    # No stop loss — Lynch's philosophy is to hold through volatility.
    "small_cap_gems": {
        "name": "Small-Cap Hidden Gems",
        "description": "Tiny, fast-growing companies before the crowd arrives",
        "use_case": "Lynch hunts the small-cap universe ($100M–$3B) for hidden gems with strong fundamentals and explosive growth runway. High risk, high reward. Lynch holds through volatility — no stop loss.",
        "filters": [
            { "field": "market_cap", "operator": ">=", "value": 100000000 },   # > $100M
            { "field": "market_cap", "operator": "<=", "value": 3000000000 },  # < $3B
            { "field": "country", "value": ["US", "CA"], "operator": "in" }
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": None,  # Lynch holds through volatility
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 5: Global Titans ────────────────────────────────────────────────
    # Lynch + Buffett · Global · Large-cap ($10B+)
    # The world's most dominant businesses. No borders, no limits.
    "global_titans": {
        "name": "Global Titans",
        "description": "The world's most dominant businesses, no borders",
        "use_case": "Lynch and Buffett together search the entire world for the most dominant large-cap businesses. No geographic constraints — if it's a great business, it qualifies.",
        "filters": [
            { "field": "market_cap", "value": 10000000000, "operator": ">=" }  # > $10B, global
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 6: Dividend Royalty ─────────────────────────────────────────────
    # Buffett solo · US-only · Large-cap ($5B+)
    # Cash-generating machines. Income-focused portfolio.
    "dividend_royalty": {
        "name": "Dividend Royalty",
        "description": "Cash-generating US giants that reward shareholders",
        "use_case": "Buffett targets large profitable US companies with strong cash flows and consistent dividend histories. A concentrated, low-turnover portfolio that pays you to hold.",
        "filters": [
            { "field": "market_cap", "operator": ">=", "value": 5000000000 },  # > $5B
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 7: Fallen Angels ────────────────────────────────────────────────
    # Lynch + Buffett · North America + Europe · Large-cap ($5B+) · Down 20%+
    # Contrarian. Great companies at temporary discounts. Veto power consensus.
    "fallen_angels": {
        "name": "Fallen Angels",
        "description": "Great businesses unfairly punished by the market",
        "use_case": "Lynch and Buffett hunt for quality large-caps across North America and Europe that have fallen 20%+ from their highs. The thesis: the business is still intact, the market is wrong. Either analyst can veto if the story is truly broken.",
        "filters": [
            { "field": "price_vs_52wk_high", "operator": "<=", "value": -20 },
            { "field": "market_cap", "operator": ">=", "value": 5000000000 },  # > $5B
            { "field": "region", "value": ["North America", "Europe"], "operator": "==" }
        ],
        "analysts": ["lynch", "buffett"],
        "consensus_mode": "veto_power",
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 8: European Value ───────────────────────────────────────────────
    # Buffett solo · Europe · Mid-to-Large ($3B+)
    # Buffett hunting underpriced quality in Europe.
    "europe_value": {
        "name": "European Value",
        "description": "Buffett hunts undervalued quality across Europe",
        "use_case": "Buffett applies his value lens to European markets, where world-class businesses often trade at persistent discounts to US peers. Focus on quality brands and dominant franchises.",
        "filters": [
            { "field": "market_cap", "value": 3000000000, "operator": ">=" },  # > $3B
            { "field": "region", "value": "Europe", "operator": "==" }
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 9: Asia Growth ──────────────────────────────────────────────────
    # Lynch solo · Asia · Mid-to-Large ($1B+)
    # Lynch scours Asia's fastest-growing economies.
    "asia_growth": {
        "name": "Asia Growth",
        "description": "Lynch finds the next wave of Asian consumer and tech winners",
        "use_case": "Lynch applies his growth radar to Asia's dynamic economies. Consumer brands, tech leaders, and industrial champions that are scaling fast across the world's most populous markets.",
        "filters": [
            { "field": "market_cap", "value": 1000000000, "operator": ">=" },  # > $1B
            { "field": "region", "value": "Asia", "operator": "==" }
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 10: Mid-Cap Momentum ───────────────────────────────────────────
    # Lynch solo · US · Mid-cap ($2B–$20B) · Within 15% of 52-week high
    # Winners keep winning. Price momentum as a qualifier.
    "mid_cap_momentum": {
        "name": "Mid-Cap Momentum",
        "description": "Mid-sized winners near their highs — strength breeds strength",
        "use_case": "Lynch focuses on US mid-caps that are holding or breaking to new highs. Price momentum signals market confidence. The opposite of Fallen Angels — buy what's working, not what's broken.",
        "filters": [
            { "field": "market_cap", "operator": ">=", "value": 2000000000 },   # > $2B
            { "field": "market_cap", "operator": "<=", "value": 20000000000 },  # < $20B
            { "field": "price_vs_52wk_high", "operator": ">=", "value": -15 },  # Within 15% of 52-week high
            { "field": "country", "value": "US", "operator": "==" }
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },

    # ── STRATEGY 11: Consumer & Tech Innovators ──────────────────────────────────
    # Lynch solo · US · Any size ($500M+) · Tech + Comms + Consumer Cyclical sectors
    # Lynch's playbook: businesses he can understand that are changing the world.
    "tech_innovators": {
        "name": "Consumer & Tech Innovators",
        "description": "Lynch finds transformative businesses you can explain to a 10-year-old",
        "use_case": "Lynch targets Technology, Communication Services, and Consumer Cyclical companies — sectors where he found his biggest winners. Focused on businesses with clear growth stories, strong brands, and real earnings.",
        "filters": [
            { "field": "market_cap", "value": 500000000, "operator": ">=" },  # > $500M
            { "field": "sector", "operator": "in", "value": ["Technology", "Communication Services", "Consumer Cyclical"] },
            { "field": "country", "value": "US", "operator": "==" }
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
            "max_positions": 25,
            "kelly_fraction": None,
            "max_position_pct": 15,
            "fixed_position_pct": None,
            "min_position_value": 500
        },
        "exit_rules": {
            "max_hold_days": None,
            "stop_loss_pct": -20,
            "profit_target_pct": 200,
            "score_degradation": {"lynch_below": 40, "buffett_below": 40}
        }
    },
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
    "lynch": ["lynch_tenbagger", "small_cap_gems", "mid_cap_momentum", "asia_growth", "tech_innovators"],
    "buffett": ["buffett_fortress", "dividend_royalty", "europe_value"],
    "both": ["dream_team", "global_titans", "fallen_angels"]
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
