{
    "name": "Forecast App",
    "author": "Computer Center",
    "summary": "Forecast App Development",
    "sequence":15,
    "depends": ["base", "mail", "crm"],
    "data": [
        "security/ir.model.access.csv",
        "security/forecast_security.xml",
        "views/forecast_views.xml",
        "views/monthly_forecast_view.xml",
        "views/weekly_forecast_view.xml",
        # "views/target_view.xml",
        "data/forecast_sequence.xml",
    ],
}