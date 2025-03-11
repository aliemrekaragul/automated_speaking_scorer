import numpy as np
from typing import List
from models.score_models import SpeakingPerformance

class ScoreAdjustmentAgent:
    def adjust_scores(self, performances: List[SpeakingPerformance]) -> List[SpeakingPerformance]:
        """
        Calculate adjusted score by summing analytic rubric domains.
        """
        # TODO: implement conversion table here when it is ready
        for perf in performances:
            if perf.analytic_scores:
                total_score = sum([
                    perf.analytic_scores.grammar,
                    perf.analytic_scores.vocabulary,
                    perf.analytic_scores.content,
                    perf.analytic_scores.fluency,
                    perf.analytic_scores.pronunciation,
                    perf.analytic_scores.overall
                ])
                perf.adjusted_score = total_score
            else:
                perf.adjusted_score = None
        
        return performances 