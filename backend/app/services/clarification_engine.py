import re

from app.schemas.analysis import QueryAnalysis
from app.schemas.clarification import ClarificationResponse, ClarificationOption


class ClarificationEngine:
    # Supported ranking metrics and the patterns that count as explicit
    # user evidence.  Each key is the canonical metric value; the list
    # holds regex patterns that match the user's original question text.
    SUPPORTED_METRICS: dict[str, list[str]] = {
        "revenue":    [r"\brevenue\b"],
        "units_sold": [r"\bunits[\s_]sold\b"],
        "rating":     [r"\brating\b"],
        "profit":     [r"\bprofit\b"],
    }

    @classmethod
    def _question_has_explicit_metric(cls, question: str) -> str | None:
        """Return the canonical metric value if the *user's original
        question* explicitly mentions a supported ranking metric.

        Returns ``None`` when no explicit metric is found — even if the
        LLM hallucinated one in ``analysis.metric``.
        """
        q_lower = question.lower()
        for metric_value, patterns in cls.SUPPORTED_METRICS.items():
            for pat in patterns:
                if re.search(pat, q_lower):
                    return metric_value
        return None

    @classmethod
    def generate(cls, analysis: QueryAnalysis) -> ClarificationResponse:
        # RULE 1 & 6: Explicit ambiguity / Do not over-clarify
        if not analysis.needs_clarification:
            return ClarificationResponse(needs_clarification=False)

        # Helper to search missing info and ambiguities
        missing_text = " ".join(analysis.missing_information + analysis.ambiguities).lower()

        # RULE 4: Missing entity
        if not analysis.entities:
            return ClarificationResponse(
                needs_clarification=True,
                clarification_type="entity",
                question="Which entity should I calculate this for?",
                options=[],
                reason="The target entity is missing."
            )

        # Determine whether this is a ranking-style query
        is_ranking = analysis.intent == "ranking" or any(
            w in analysis.question.lower() for w in ["best", "top"]
        )

        # Check whether the user's ORIGINAL question text contains an
        # explicit supported metric — do NOT trust analysis.metric alone,
        # because the LLM may have hallucinated / inferred it.
        explicit_metric = cls._question_has_explicit_metric(analysis.question)

        # RULE 2: Ranking metric ambiguity — trigger clarification when
        # the user did NOT explicitly state a metric in the question.
        if is_ranking and not explicit_metric:
            return ClarificationResponse(
                needs_clarification=True,
                clarification_type="ranking_metric",
                question=(
                    "What do you mean by 'best products'?"
                    if "product" in analysis.question.lower()
                    else "What metric should I use for ranking?"
                ),
                options=[
                    ClarificationOption(label="Highest revenue", value="revenue"),
                    ClarificationOption(label="Most units sold", value="units_sold"),
                    ClarificationOption(label="Highest rating", value="rating"),
                    ClarificationOption(label="Highest profit", value="profit"),
                ],
                reason="The ranking metric is missing."
            )

        # RULE 3: Time range ambiguity
        if any(kw in missing_text for kw in ["time", "date", "period"]):
            return ClarificationResponse(
                needs_clarification=True,
                clarification_type="time_range",
                question="What time period would you like?",
                options=[
                    ClarificationOption(label="Today", value="today"),
                    ClarificationOption(label="This week", value="this_week"),
                    ClarificationOption(label="This month", value="this_month"),
                    ClarificationOption(label="This year", value="this_year"),
                ],
                reason="A time range is missing."
            )

        # OVERRIDE: If it's a ranking query with an explicit metric in
        # the user's question AND entities are present, the LLM's
        # uncertainty is a false positive — proceed without clarification.
        if is_ranking and explicit_metric and analysis.entities:
            return ClarificationResponse(needs_clarification=False)

        # RULE 5: Existing analyzer-generated clarification
        # If we got here, it means needs_clarification is True but we didn't hit our specific rules.
        # Preserve the analyzer's ambiguity reasoning in an open-ended clarification.
        reason = analysis.ambiguities[0] if analysis.ambiguities else (analysis.missing_information[0] if analysis.missing_information else "The query is ambiguous.")
        return ClarificationResponse(
            needs_clarification=True,
            clarification_type="generic",
            question="Could you clarify your request?",
            options=[],
            reason=reason
        )

