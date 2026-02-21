# ABOUTME: Scenario-based tests for strategy execution pipeline behavior
# ABOUTME: Verifies outcomes of deliberation, thesis filtering, and exit routing

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import pandas as pd

from strategy_executor import StrategyExecutor, ExitSignal
from strategy_executor.consensus import ConsensusEngine
from strategy_executor.deliberation import DeliberationMixin


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

def make_enriched_stock(symbol, lynch_score=75, buffett_score=75,
                        lynch_status='BUY', buffett_status='BUY',
                        lynch_thesis=None, buffett_thesis=None,
                        lynch_thesis_verdict=None, buffett_thesis_verdict=None,
                        position_type='new'):
    """Build a stock dict matching the output of Phase 2+3 (scored + thesis)."""
    return {
        'symbol': symbol,
        'position_type': position_type,
        'lynch_score': lynch_score,
        'lynch_status': lynch_status,
        'buffett_score': buffett_score,
        'buffett_status': buffett_status,
        'lynch_thesis': lynch_thesis,
        'buffett_thesis': buffett_thesis,
        'lynch_thesis_verdict': lynch_thesis_verdict,
        'buffett_thesis_verdict': buffett_thesis_verdict,
    }


def make_mock_db():
    """Create a mock DB with all methods deliberation needs."""
    db = Mock()
    db.create_strategy_decision = Mock(return_value=1)
    db.append_to_run_log = Mock()
    return db


def make_deliberation_executor(db=None):
    """Build a StrategyExecutor with mocked-out dependencies for deliberation tests."""
    db = db or make_mock_db()
    executor = StrategyExecutor.__new__(StrategyExecutor)
    executor.db = db
    executor.consensus_engine = ConsensusEngine()
    executor.position_sizer = Mock()
    executor.exit_checker = Mock()
    executor.benchmark_tracker = Mock()
    executor.universe_filter = Mock()
    executor._analyst = Mock()
    executor._lynch_criteria = Mock()
    return executor


# ═══════════════════════════════════════════════════════════════════════
# Scenario: Multi-analyst deliberation with both theses
# ═══════════════════════════════════════════════════════════════════════

class TestDeliberationWithBothTheses:
    """When both Lynch and Buffett have generated theses,
    deliberation determines the final BUY/AVOID/WATCH verdict."""

    def test_both_analysts_say_buy_and_deliberation_agrees(self):
        """Given both analysts wrote BUY theses,
        when deliberation returns BUY,
        then the stock becomes a buy decision."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=80, buffett_score=85,
            lynch_thesis='Lynch says BUY', buffett_thesis='Buffett says BUY',
            lynch_thesis_verdict='BUY', buffett_thesis_verdict='BUY')

        with patch.object(executor, '_conduct_deliberation',
                          return_value=('Agreed: BUY', 'BUY')):
            buys, exits, holds = executor._deliberate(
                enriched=[stock], run_id=1,
                conditions={'thesis_verdict_required': ['BUY']},
                strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
                analysts=['lynch', 'buffett'])

        assert len(buys) == 1
        assert buys[0]['symbol'] == 'AAPL'
        assert len(exits) == 0

    def test_neither_analyst_bullish_skips_deliberation(self):
        """Given neither analyst wrote a BUY thesis,
        when deliberation is attempted,
        then the stock is skipped without calling the AI deliberation."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=80, buffett_score=75,
            lynch_thesis='Lynch says WATCH', buffett_thesis='Buffett says WATCH',
            lynch_thesis_verdict='WATCH', buffett_thesis_verdict='WATCH')

        with patch.object(executor, '_conduct_deliberation') as mock_delib:
            buys, exits, holds = executor._deliberate(
                enriched=[stock], run_id=1,
                conditions={'thesis_verdict_required': ['BUY']},
                strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
                analysts=['lynch', 'buffett'])

        # AI deliberation should NOT have been called
        mock_delib.assert_not_called()
        assert len(buys) == 0

    def test_deliberation_verdict_avoid_on_held_stock_emits_exit(self):
        """Given a held stock where deliberation returns AVOID,
        when the stock is held in portfolio,
        then an ExitSignal is emitted."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=45, buffett_score=50,
            lynch_thesis='Lynch says AVOID', buffett_thesis='Buffett says BUY',
            lynch_thesis_verdict='AVOID', buffett_thesis_verdict='BUY')

        with patch.object(executor, '_conduct_deliberation',
                          return_value=('Disagree: AVOID', 'AVOID')):
            buys, exits, holds = executor._deliberate(
                enriched=[stock], run_id=1,
                conditions={},
                strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
                held_symbols={'AAPL'},
                holdings={'AAPL': 100},
                analysts=['lynch', 'buffett'])

        assert len(buys) == 0
        assert len(exits) == 1
        assert exits[0].symbol == 'AAPL'
        assert exits[0].quantity == 100

    def test_neither_bullish_with_avoid_on_held_emits_exit(self):
        """Given a held stock where one analyst says AVOID and neither says BUY,
        when deliberation is skipped (short-circuit),
        then an exit signal is still emitted."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=45, buffett_score=50,
            lynch_thesis='Lynch says AVOID', buffett_thesis='Buffett says WATCH',
            lynch_thesis_verdict='AVOID', buffett_thesis_verdict='WATCH')

        buys, exits, holds = executor._deliberate(
            enriched=[stock], run_id=1,
            conditions={},
            strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
            held_symbols={'AAPL'},
            holdings={'AAPL': 50},
            analysts=['lynch', 'buffett'])

        assert len(exits) == 1
        assert exits[0].symbol == 'AAPL'
        assert exits[0].quantity == 50


# ═══════════════════════════════════════════════════════════════════════
# Scenario: Consensus VETO stops deliberation immediately
# ═══════════════════════════════════════════════════════════════════════

class TestConsensusVetoStopsDeliberation:

    def test_veto_on_new_stock_produces_no_decisions(self):
        """Given a stock where consensus engine returns VETO,
        when the stock is a new candidate (not held),
        then no buy decision and no exit signal are produced."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=20, buffett_score=25,
            lynch_status='AVOID', buffett_status='CAUTION',
            lynch_thesis='bad', buffett_thesis='also bad',
            lynch_thesis_verdict='AVOID', buffett_thesis_verdict='AVOID')

        buys, exits, holds = executor._deliberate(
            enriched=[stock], run_id=1,
            conditions={'veto_score_threshold': 30},
            strategy={'consensus_mode': 'veto_power', 'consensus_threshold': 70},
            held_symbols=set(),
            analysts=['lynch', 'buffett'])

        assert len(buys) == 0
        assert len(exits) == 0

    def test_veto_on_held_stock_emits_exit(self):
        """Given a held stock where consensus engine returns VETO,
        when the stock is currently held,
        then an ExitSignal is emitted."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=20, buffett_score=25,
            lynch_status='AVOID', buffett_status='CAUTION',
            lynch_thesis='bad', buffett_thesis='also bad',
            lynch_thesis_verdict='AVOID', buffett_thesis_verdict='AVOID')

        buys, exits, holds = executor._deliberate(
            enriched=[stock], run_id=1,
            conditions={'veto_score_threshold': 30},
            strategy={'consensus_mode': 'veto_power', 'consensus_threshold': 70},
            held_symbols={'AAPL'},
            holdings={'AAPL': 200},
            analysts=['lynch', 'buffett'])

        assert len(exits) == 1
        assert exits[0].symbol == 'AAPL'
        assert exits[0].quantity == 200
        assert 'VETO' in exits[0].reason


# ═══════════════════════════════════════════════════════════════════════
# Scenario: Held stocks with failing addition scores route correctly
# ═══════════════════════════════════════════════════════════════════════

class TestHeldStocksWithFailingScores:
    """Held stocks that fail addition thresholds still go through deliberation.
    If analysts say BUY, they become HOLD (not a new buy); if AVOID, they exit."""

    def test_failing_held_stock_with_buy_verdict_becomes_hold(self):
        """Given a held stock that failed addition scoring but got BUY from deliberation,
        when processed through deliberation,
        then it goes to held_verdicts (not buy_decisions) — it's a HOLD, not an addition."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=55, buffett_score=50,
            position_type='held_exit_evaluation',
            lynch_thesis='Lynch reaffirms', buffett_thesis='Buffett agrees',
            lynch_thesis_verdict='BUY', buffett_thesis_verdict='BUY')

        with patch.object(executor, '_conduct_deliberation',
                          return_value=('Reaffirmed: BUY', 'BUY')):
            buys, exits, holds = executor._deliberate(
                enriched=[stock], run_id=1,
                conditions={'thesis_verdict_required': ['BUY']},
                strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
                held_symbols={'AAPL'},
                holdings={'AAPL': 100},
                symbols_of_held_stocks_with_failing_scores={'AAPL'},
                analysts=['lynch', 'buffett'])

        assert len(buys) == 0  # NOT a buy
        assert len(exits) == 0
        assert len(holds) == 1
        assert holds[0]['symbol'] == 'AAPL'
        assert holds[0]['final_verdict'] == 'BUY'

    def test_failing_held_stock_with_avoid_verdict_exits(self):
        """Given a held stock that failed addition scoring and got AVOID from deliberation,
        when processed through deliberation,
        then an ExitSignal is emitted."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=35, buffett_score=40,
            position_type='held_exit_evaluation',
            lynch_thesis='Lynch says sell', buffett_thesis='Buffett says BUY',
            lynch_thesis_verdict='AVOID', buffett_thesis_verdict='BUY')

        with patch.object(executor, '_conduct_deliberation',
                          return_value=('Disagreed: AVOID', 'AVOID')):
            buys, exits, holds = executor._deliberate(
                enriched=[stock], run_id=1,
                conditions={},
                strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
                held_symbols={'AAPL'},
                holdings={'AAPL': 75},
                symbols_of_held_stocks_with_failing_scores={'AAPL'},
                analysts=['lynch', 'buffett'])

        assert len(buys) == 0
        assert len(exits) == 1
        assert exits[0].symbol == 'AAPL'
        assert exits[0].quantity == 75


# ═══════════════════════════════════════════════════════════════════════
# Scenario: Thesis verdict filtering
# ═══════════════════════════════════════════════════════════════════════

class TestThesisVerdictFiltering:
    """thesis_verdict_required controls which verdicts can become buy decisions."""

    def test_watch_verdict_filtered_when_only_buy_required(self):
        """Given thesis_verdict_required=['BUY'] and deliberation returns WATCH,
        when processed, then no buy decision is made."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=80, buffett_score=75,
            lynch_thesis='Cautious buy', buffett_thesis='Maybe later',
            lynch_thesis_verdict='BUY', buffett_thesis_verdict='WATCH')

        with patch.object(executor, '_conduct_deliberation',
                          return_value=('Cautious: WATCH', 'WATCH')):
            buys, exits, holds = executor._deliberate(
                enriched=[stock], run_id=1,
                conditions={'thesis_verdict_required': ['BUY']},
                strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
                analysts=['lynch', 'buffett'])

        assert len(buys) == 0

    def test_buy_verdict_passes_filter(self):
        """Given thesis_verdict_required=['BUY'] and deliberation returns BUY,
        when processed, then a buy decision is made."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=85, buffett_score=80,
            lynch_thesis='Strong buy case', buffett_thesis='Agree to buy',
            lynch_thesis_verdict='BUY', buffett_thesis_verdict='BUY')

        with patch.object(executor, '_conduct_deliberation',
                          return_value=('Consensus: BUY', 'BUY')):
            buys, exits, holds = executor._deliberate(
                enriched=[stock], run_id=1,
                conditions={'thesis_verdict_required': ['BUY']},
                strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
                analysts=['lynch', 'buffett'])

        assert len(buys) == 1
        assert buys[0]['symbol'] == 'AAPL'


# ═══════════════════════════════════════════════════════════════════════
# Scenario: Single-analyst strategies (no deliberation debate)
# ═══════════════════════════════════════════════════════════════════════

class TestSingleAnalystDeliberation:
    """When only one analyst is active, deliberation uses the thesis
    verdict directly — no AI debate between Lynch and Buffett."""

    def test_single_analyst_buy_becomes_buy_decision(self):
        """Given a single analyst with BUY thesis verdict,
        when deliberated, then the stock becomes a buy decision."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=80, buffett_score=0,
            lynch_status='BUY', buffett_status='N/A',
            lynch_thesis='Strong buy', lynch_thesis_verdict='BUY')

        buys, exits, holds = executor._deliberate(
            enriched=[stock], run_id=1,
            conditions={'thesis_verdict_required': ['BUY']},
            strategy={'consensus_threshold': 70},
            analysts=['lynch'])

        assert len(buys) == 1
        assert buys[0]['symbol'] == 'AAPL'

    def test_single_analyst_avoid_on_held_emits_exit(self):
        """Given a single analyst with AVOID thesis verdict on a held stock,
        when deliberated, then an exit signal is emitted."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=35, buffett_score=0,
            lynch_status='AVOID', buffett_status='N/A',
            lynch_thesis='Time to sell', lynch_thesis_verdict='AVOID')

        buys, exits, holds = executor._deliberate(
            enriched=[stock], run_id=1,
            conditions={},
            strategy={'consensus_threshold': 70},
            held_symbols={'AAPL'},
            holdings={'AAPL': 50},
            analysts=['lynch'])

        assert len(buys) == 0
        assert len(exits) == 1
        assert exits[0].symbol == 'AAPL'

    def test_single_analyst_watch_on_held_goes_to_held_verdicts(self):
        """Given a single analyst with WATCH thesis verdict on a held stock,
        when deliberated, then the stock goes to held_verdicts for rebalancing."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=60, buffett_score=0,
            lynch_status='BUY', buffett_status='N/A',
            lynch_thesis='Hold for now', lynch_thesis_verdict='WATCH')

        buys, exits, holds = executor._deliberate(
            enriched=[stock], run_id=1,
            conditions={},
            strategy={'consensus_threshold': 70},
            held_symbols={'AAPL'},
            holdings={'AAPL': 50},
            analysts=['lynch'])

        assert len(buys) == 0
        assert len(exits) == 0
        assert len(holds) == 1
        assert holds[0]['symbol'] == 'AAPL'


# ═══════════════════════════════════════════════════════════════════════
# Scenario: Mixed portfolio — multiple stocks through deliberation
# ═══════════════════════════════════════════════════════════════════════

class TestMixedPortfolioScenario:
    """Realistic scenario: 3 stocks go through deliberation with different outcomes."""

    def test_three_stocks_different_outcomes(self):
        """Given:
          - AAPL: new candidate, both analysts BUY → deliberation BUY
          - MSFT: held stock, failing scores, analysts reaffirm BUY → HOLD (not addition)
          - GOOGL: held stock, analysts say AVOID → exit

        When all three go through deliberation,
        then: 1 buy (AAPL), 1 exit (GOOGL), 1 held_verdict (MSFT)."""
        executor = make_deliberation_executor()

        aapl = make_enriched_stock(
            'AAPL', lynch_score=85, buffett_score=80,
            lynch_thesis='Strong fundamentals', buffett_thesis='Great moat',
            lynch_thesis_verdict='BUY', buffett_thesis_verdict='BUY')

        msft = make_enriched_stock(
            'MSFT', lynch_score=55, buffett_score=50,
            position_type='held_exit_evaluation',
            lynch_thesis='Still decent', buffett_thesis='Overvalued but hold',
            lynch_thesis_verdict='BUY', buffett_thesis_verdict='WATCH')

        googl = make_enriched_stock(
            'GOOGL', lynch_score=40, buffett_score=35,
            lynch_thesis='Deteriorating', buffett_thesis='Sell now',
            lynch_thesis_verdict='AVOID', buffett_thesis_verdict='AVOID')

        def mock_deliberation(user_id, symbol, **kwargs):
            verdicts = {
                'AAPL': ('Both agree: BUY', 'BUY'),
                'MSFT': ('Reaffirmed: BUY', 'BUY'),
            }
            return verdicts.get(symbol, ('Unknown', 'WATCH'))

        with patch.object(executor, '_conduct_deliberation',
                          side_effect=mock_deliberation):
            buys, exits, holds = executor._deliberate(
                enriched=[aapl, msft, googl], run_id=1,
                conditions={'thesis_verdict_required': ['BUY']},
                strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
                held_symbols={'MSFT', 'GOOGL'},
                holdings={'MSFT': 100, 'GOOGL': 50},
                symbols_of_held_stocks_with_failing_scores={'MSFT'},
                analysts=['lynch', 'buffett'])

        buy_symbols = [b['symbol'] for b in buys]
        exit_symbols = [e.symbol for e in exits]
        hold_symbols = [h['symbol'] for h in holds]

        assert buy_symbols == ['AAPL']
        assert 'GOOGL' in exit_symbols
        assert 'MSFT' in hold_symbols


# ═══════════════════════════════════════════════════════════════════════
# Scenario: Disabled strategy skips execution
# ═══════════════════════════════════════════════════════════════════════

class TestDisabledStrategy:

    def test_disabled_strategy_returns_skipped(self):
        """Given a strategy that is disabled,
        when execute_strategy is called,
        then it returns immediately with status='skipped'."""
        db = make_mock_db()
        db.get_strategy = Mock(return_value={'id': 1, 'enabled': False})

        executor = StrategyExecutor(db)
        result = executor.execute_strategy(strategy_id=1)

        assert result['status'] == 'skipped'
        assert 'disabled' in result['reason'].lower()

    def test_missing_strategy_raises(self):
        """Given a strategy ID that doesn't exist,
        when execute_strategy is called,
        then it raises ValueError."""
        db = make_mock_db()
        db.get_strategy = Mock(return_value=None)

        executor = StrategyExecutor(db)
        with pytest.raises(ValueError, match="not found"):
            executor.execute_strategy(strategy_id=999)


# ═══════════════════════════════════════════════════════════════════════
# Scenario: No theses available — strictly requires AI deliberation
# ═══════════════════════════════════════════════════════════════════════

class TestNoThesesSkipsToDecision:

    def test_missing_theses_produces_skip(self):
        """Given a stock with scores but no theses generated,
        when deliberation processes it,
        then no buy decision or exit is produced."""
        executor = make_deliberation_executor()

        stock = make_enriched_stock(
            'AAPL', lynch_score=80, buffett_score=75,
            lynch_thesis=None, buffett_thesis=None)

        buys, exits, holds = executor._deliberate(
            enriched=[stock], run_id=1,
            conditions={},
            strategy={'consensus_mode': 'both_agree', 'consensus_threshold': 70},
            analysts=['lynch', 'buffett'])

        assert len(buys) == 0
        assert len(exits) == 0
