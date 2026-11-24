# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "gem_portal_bid"
app_title = "Erpnext Gem Portal Bid Contract Engine"
app_publisher = "Shyamkumar Pandey"
app_description = "Erpnext Gem Portal Bid Contract Engine - Enterprise Multi-DocType Solution for Frappe & ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/gem_portal_bid/css/gem_portal_bid.bundle.css"
app_include_js = "/assets/gem_portal_bid/js/gem_portal_bid.bundle.js"

# Document Events
# ---------------
doc_events = {
    "Erpnext Gem Portal Bid Contract Engine Entry": {
        "validate": "gem_portal_bid.services.validator.EnterpriseValidationEngine.validate_compliance_rules",
        "on_submit": "gem_portal_bid.services.integration_service.EnterpriseIntegrationService.verify_remote_status"
    }
}

# Scheduled Background Tasks
# --------------------------
scheduler_events = {
    "hourly": [
        "gem_portal_bid.tasks.hourly_sync"
    ],
    "daily": [
        "gem_portal_bid.tasks.daily_reconciliation"
    ],
    "weekly": [
        "gem_portal_bid.tasks.weekly_digest"
    ]
}
