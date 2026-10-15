import pandas as pd


BLOCKING_STATES = {
    "BLOCK",
    "BLOCK_AND_REPORT",
    "ENABLE_AND_REPORT",
}

ENABLED_STATES = {
    "ACTIVE",
    "ENABLE",
    "ENABLED",
    "TRUE",
    "CONFIGURED",
}

REPORT_ONLY_STATES = {
    "PASSIVE",
    "REPORT_ONLY",
}

DISABLED_STATES = {
    "DISABLE",
    "DISABLED",
    "FALSE",
    "NOT_CONFIGURED",
}

UNKNOWN_STATES = {
    "",
    "N/A",
    "NA",
    "NONE",
    "NULL",
    "UNKNOWN",
}


def classify_feature_state(value):
    if isinstance(value, bool):
        return "enabled" if value else "disabled"

    if value is None:
        return "unknown"

    normalized = str(value).strip().upper().replace(" ", "_").replace("-", "_")

    if normalized in BLOCKING_STATES:
        return "blocking"
    if normalized in ENABLED_STATES:
        return "enabled"
    if normalized in REPORT_ONLY_STATES:
        return "report_only"
    if normalized in DISABLED_STATES:
        return "disabled"
    if normalized in UNKNOWN_STATES:
        return "unknown"

    return "unknown"


def is_disabled(value):
    return classify_feature_state(value) == "disabled"


def is_report_only(value):
    return classify_feature_state(value) == "report_only"


def is_enabled(value):
    return classify_feature_state(value) in {"blocking", "enabled", "report_only"}


def _meets_target(state, requires_blocking):
    if requires_blocking:
        return state == "blocking"

    return state in {"blocking", "enabled", "report_only"}


def calculate_waf_progress(
    adoption_df,
    licensed_modules,
    blocking_modules=None,
    application_ids=None,
    application_capacity=0,
):
    blocking_modules = set(blocking_modules or [])
    licensed_modules = list(dict.fromkeys(licensed_modules or []))
    app_df = adoption_df

    if "Application ID" in app_df.columns:
        app_df = app_df.drop_duplicates(subset=["Application ID"])

    if application_ids is not None and "Application ID" in app_df.columns:
        app_df = app_df[app_df["Application ID"].isin(application_ids)]

    application_count = len(app_df)
    expected_checks = application_count * len(licensed_modules)
    completed_checks = 0
    missing_checks = 0
    unknown_checks = 0
    application_rows = []

    for _, app in app_df.iterrows():
        app_completed = 0
        app_missing = 0
        app_unknown = 0
        missing_modules = []
        unknown_modules = []

        for module in licensed_modules:
            state = classify_feature_state(app.get(module))
            is_complete = _meets_target(state, module in blocking_modules)

            if is_complete:
                completed_checks += 1
                app_completed += 1
            elif state == "unknown":
                unknown_checks += 1
                app_unknown += 1
                unknown_modules.append(module)
            else:
                missing_checks += 1
                app_missing += 1
                missing_modules.append(module)

        app_percent = (
            round(app_completed / len(licensed_modules) * 100, 1)
            if licensed_modules
            else None
        )

        application_rows.append({
            "Application Name": app.get("Application Name", "Unknown Application"),
            "Application ID": app.get("Application ID"),
            "Progress": app_percent,
            "Completed": app_completed,
            "Missing": app_missing,
            "Unconfirmed": app_unknown,
            "Missing Features": ", ".join(missing_modules),
            "Unconfirmed Features": ", ".join(unknown_modules),
        })

    progress_percent = (
        round(completed_checks / expected_checks * 100, 1)
        if expected_checks
        else None
    )
    capacity_percent = (
        round(application_count / application_capacity * 100, 1)
        if application_capacity > 0
        else None
    )

    return {
        "application_count": application_count,
        "licensed_application_capacity": application_capacity,
        "capacity_percent": capacity_percent,
        "licensed_feature_count": len(licensed_modules),
        "expected_checks": expected_checks,
        "completed_checks": completed_checks,
        "missing_checks": missing_checks,
        "unknown_checks": unknown_checks,
        "progress_percent": progress_percent,
        "applications": pd.DataFrame(application_rows),
    }
