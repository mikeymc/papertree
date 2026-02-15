# ABOUTME: Package entry point composing LynchCriteria from mixin classes.
# ABOUTME: Re-exports the composed class plus scoring constants and related classes.

from scoring.core import LynchCriteriaCore, SCORE_THRESHOLDS
from scoring.scoring_mixins import ScoringMixin
from scoring.batch import BatchScoringMixin
from scoring.vectors import StockVectors, DEFAULT_ALGORITHM_CONFIG
from scoring.evaluator import StockEvaluator


class LynchCriteria(LynchCriteriaCore, ScoringMixin, BatchScoringMixin):
    pass
