import hashlib

import streamlit as st


BASE_COLUMNS = [
    "Application Name",
    "Application ID",
    "Deployment Status",
    "Security Policy Applied",
    "Security Policy Name",
    "Data Source",
]

LICENSE_FEATURES = [
    "RFC Violation Protection",
    "Signature Protection",
    "SQL Injection",
    "Path Access",
    "JSON Validation",
    "SSRF",
    "Access Control",
    "Geo Blocking",
    "Security Bypass",
    "Anonymous Proxy / TOR",
    "Source Blocking",
    "ERT Feed",
    "HTTP Protection / Rules",
    "Bot Manager",
    "API Protection",
    "ATO",
    "Rate Limit",
    "API Discovery",
    "BLA Protection",
    "Export Security Logs",
    "Export Access Logs",
    "GraphQL",
    "CDN",
    "Client-side Protection",
    "Web DDoS",
]


def get_account_settings_key(context):
    account = context.strip() if context else ""
    digest = hashlib.sha256(account.encode("utf-8")).hexdigest()[:12]
    return f"account_{digest}" if account else "account_unassigned"


def render_entitlement_selector(context):
    settings_key = get_account_settings_key(context)

    st.sidebar.divider()
    st.sidebar.subheader("Manual License Settings")

    st.sidebar.number_input(
        "Licensed application capacity",
        min_value=0,
        value=0,
        step=1,
        key=f"licensed_application_capacity_{settings_key}",
        help="Enter the maximum number of applications covered by the license. Zero means not provided.",
    )

    licensed_modules = st.sidebar.multiselect(
        "Licensed WAF features",
        LICENSE_FEATURES,
        key=f"licensed_modules_selection_{settings_key}",
        help="Select only the features included in this customer's license.",
    )

    blocking_key = f"blocking_modules_selection_{settings_key}"
    blocking_modules = st.session_state.get(blocking_key, [])
    if any(module not in licensed_modules for module in blocking_modules):
        st.session_state[blocking_key] = [
            module for module in blocking_modules if module in licensed_modules
        ]

    st.sidebar.multiselect(
        "Features that must be in Blocking mode",
        licensed_modules,
        key=blocking_key,
        help="Other selected features are measured as enabled/configured; Report Only and Passive count as active for those features.",
    )

    st.session_state["licensed_modules"] = licensed_modules
    st.session_state["blocking_modules"] = [
        module
        for module in st.session_state[blocking_key]
        if module in licensed_modules
    ]
    st.session_state["licensed_application_capacity"] = st.session_state[
        f"licensed_application_capacity_{settings_key}"
    ]

    return settings_key


def filter_columns_by_entitlement(df):
    licensed_modules = st.session_state.get("licensed_modules", [])
    allowed_columns = set(BASE_COLUMNS + licensed_modules)
    return df[[column for column in df.columns if column in allowed_columns]]


def is_module_licensed(module_name):
    return module_name in st.session_state.get("licensed_modules", [])
