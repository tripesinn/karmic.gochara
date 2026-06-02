"""
blueprints — Flask blueprints for Karmic Gochara (v2)

12 blueprints, 40 routes extraites de app.py (3094→60 lignes)

public    /, /sw.js, /privacy, /.well-known/assetlinks.json
auth      /login, /register, /logout, /set_lang
astro     /calculate, /v2/calculate, /chart/*, /hook/transit, /synthesis/prompt
chat      /chat/status, /chat/ask, /chat/summarize
alerts    /toggle_alerts, /alert/*, /api/v1/alert*, /api/v1/transit-alert
calendar  /calendar, /report/annual
cron      /cron/daily
email     /send_synthesis, /save_email, /expand
payments  /stripe/*, /api/complete_payment
api       /api/profile, /api/plan_check, /api/v1/karmic-analysis, /api/prefetch_year
data      /rate_synthesis, /content/daily, /generate_task
geocode   /geocode
"""
