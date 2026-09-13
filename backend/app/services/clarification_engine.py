from app.schemas.analysis import QueryAnalysis
from app.schemas.clarification import ClarificationResponse, ClarificationOption

class ClarificationEngine:
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

        # RULE 2: Ranking metric ambiguity
        is_ranking = analysis.intent == "ranking" or any(w in analysis.question.lower() for w in ["best", "top"])
        is_ambiguous_ranking = is_ranking and not analysis.metric
        if is_ambiguous_ranking:
            return ClarificationResponse(
                needs_clarification=True,
                clarification_type="ranking_metric",
                question="What do you mean by 'best products'?" if "product" in analysis.question.lower() else "What metric should I use for ranking?",
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
            
        # OVERRIDE: If it's a ranking query that has an explicit metric and entities, 
        # the LLM's uncertainty is likely a false positive. We can proceed.
        if is_ranking and analysis.metric and analysis.entities:
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
