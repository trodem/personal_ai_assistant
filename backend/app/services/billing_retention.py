from app.api.schemas import CancelPreviewResponse, RetentionStatusResponse


def build_cancel_preview(*, reason: str) -> CancelPreviewResponse:
    if reason == "too_expensive":
        return CancelPreviewResponse(
            can_pause=True,
            can_downgrade=True,
            suggested_offer="20% off for 2 months",
            impact_summary="Downgrading to free keeps core memory and question features with limits.",
        )
    if reason == "not_using_enough":
        return CancelPreviewResponse(
            can_pause=True,
            can_downgrade=True,
            suggested_offer="Pause plan for 1 month",
            impact_summary="Pausing keeps your data and avoids immediate cancellation.",
        )
    return CancelPreviewResponse(
        can_pause=True,
        can_downgrade=True,
        suggested_offer="Try free plan first",
        impact_summary="Cancellation removes premium benefits while preserving account data.",
    )


def build_retention_status(*, subscription_plan: str) -> RetentionStatusResponse:
    if subscription_plan == "premium":
        return RetentionStatusResponse(
            churn_risk="medium",
            recommended_actions=[
                "show_cancel_preview",
                "offer_temporary_discount",
            ],
        )
    return RetentionStatusResponse(
        churn_risk="low",
        recommended_actions=[
            "promote_premium_value",
            "encourage_feature_adoption",
        ],
    )
