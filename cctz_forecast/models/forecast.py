from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import logging
import calendar

_logger = logging.getLogger(__name__)


class Forecast(models.Model):
    _name = "cctz.forecast"
    _description = "Forecast App for Sales and Pre Sales"
    _inherit = ["mail.thread"]

    forecast_number = fields.Char(
        string="Forecast Number",
        copy=False,
        readonly=True,
        required=True,
        store=True,
        default=lambda self: _("New"),
    )
    target_number = fields.Char(string="Target Number", copy=False, readonly=True, store=True, default=lambda self: _("New"))
    target_amount = fields.Float("Target Amount")
    target_gp = fields.Float("Target GP")
    user_id = fields.Many2one(
        "res.users",
        string="Forecast User",
        store=True,
        default=lambda self: self.env.uid,
        readonly=True,
    )
    target_user_id = fields.Many2one(
        "res.users",
        string="Forecast User",
        store=True,
        default=lambda self: self.env.uid,
        readonly=True,
    )
    month = fields.Selection(
        [
            ("01", "January"),
            ("02", "February"),
            ("03", "March"),
            ("04", "April"),
            ("05", "May"),
            ("06", "June"),
            ("07", "July"),
            ("08", "August"),
            ("09", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        string="Month",
        required=True,
        default=lambda self: self._default_month(),
        readonly=True,
    )
    year = fields.Selection(
        [(str(num), str(num)) for num in range(2020, 2031)],
        string="Year",
        required=True,
        default=lambda self: self._default_year(),
        readonly=True,
    )

    week = fields.Selection(
        [
            ("1", "Week 1"),
            ("2", "Week 2"),
            ("3", "Week 3"),
            ("4", "Week 4"),
            ("5", "Week 5"),
        ],
        string="Week",
        compute="_compute_week",
        store=True
    )
    week_date = fields.Date(
        string="Date",
        default=fields.Date.context_today,
        store=True,
        readonly=True
    )
    forecast_type = fields.Selection(
        [("weekly", "Weekly"), ("monthly", "Monthly")],
        string="Forecast Type",
        required=True,
        default="weekly",
        readonly=True,
    )
    forecast_amount = fields.Float(string="Forecast Amount", required=True)
    forecast_gp = fields.Float(string="Forecast GP", required=True)
    actual_amount = fields.Float(string="Actual Amount", required=True)
    actual_gp = fields.Float(string="Actual GP", required=True)
    total_expected_revenue = fields.Float(
        string="Total Expected Revenue",
        compute="_compute_total_expected_revenue",
        store=True,
        readonly=False,
    )
    unit_id = fields.Many2one(
        "hr.department",
        string="Business Unit",
        related="user_id.department_id",
        store=True,
    )

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.forecast_number}"
            result.append((record.id, name))
        return result
    
    def target_name_get(self):
        result = []
        for record in self:
            name = f'{record.target_number}'
            result.append((record.id, name))
        return result

    @api.model
    def _default_month(self):
        return datetime.now().strftime("%m")

    @api.model
    def _default_year(self):
        return str(datetime.now().year)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            forecast_type = vals.get("forecast_type")
            today = datetime.today()
            current_day = today.weekday()
            if not forecast_type:
                forecast_type = self._context.get("default_forecast_type", "weekly")
                vals["forecast_type"] = forecast_type
            if forecast_type == "weekly" and current_day > 0:
                raise ValidationError(
                    _("You cannot add a new weekly forecast after Monday of the week.")
                )
            if forecast_type == "monthly":
                start_date = datetime(today.year, today.month, 1)
                end_date = datetime(today.year, today.month, 6)
                if not (start_date <= today <= end_date):
                    raise ValidationError(
                        _(
                            "Monthly forecast can only be added from the 1st to the 6th of the month."
                        )
                    )
            if vals.get("forecast_number", _("New")) == _("New"):
                vals["forecast_number"] = self.env["ir.sequence"].next_by_code(
                    "cctz.forecast"
                ) or _("New")
            if forecast_type == "weekly" and not vals.get("week"):
                vals["week"] = "1"

        return super(Forecast, self).create(vals_list)

    @api.model
    def default_get(self, fields_list):
        defaults = super(Forecast, self).default_get(fields_list)
        if self.env.context.get("default_forecast_type"):
            defaults["forecast_type"] = self.env.context.get("default_forecast_type")
        return defaults

    @api.constrains("forecast_amount", "forecast_gp")
    def _check_modify_deadline(self):
        """Allow modification of forecast amounts after the deadline"""
        current_day = datetime.now().weekday()
        if self.forecast_type == "weekly" and current_day > 0:
            _logger.info(
                "Modification allowed for forecast amount and GP after Monday."
            )

    # @api.constrains("actual_amount", "actual_gp")
    # def _check_actual(self):
    #     """Ensure that actuals are added only on Mondays for weekly,
    #     and by the 6th of the following month for monthly forecasts."""
    #     today = datetime.today()
    #     if self.forecast_type == "weekly":
    #         if today.weekday() != 0:
    #             raise ValidationError(
    #                 _(
    #                     "You can only add actual amounts and GP for weekly forecasts on Mondays."
    #                 )
    #             )
    #         for record in self:
    #             forecast_week = int(record.week) if record.week else 0
    #             current_week = (today - timedelta(days=today.weekday())).isocalendar()[
    #                 1
    #             ]
    #             if forecast_week != current_week - 1:
    #                 raise ValidationError(
    #                     _(
    #                         "You can only add actuals for the past week. The current forecast is for week %s, and you are adding actuals for the wrong week."
    #                         % forecast_week
    #                     )
    #                 )
    #     elif self.forecast_type == "monthly":
    #         for record in self:
    #             first_day_of_next_month = datetime(
    #                 today.year, today.month, 1
    #             ) + timedelta(days=32)
    #             first_day_of_next_month = first_day_of_next_month.replace(day=1)
    #             sixth_day_of_next_month = datetime(today.year, today.month, 6)
    #             if today > sixth_day_of_next_month:
    #                 raise ValidationError(
    #                     _(
    #                         "You cannot add or edit actuals after the 6th day of the month following the forecast's creation."
    #                     )
    #                 )



    @api.depends("user_id")
    def _compute_total_expected_revenue(self):
        for record in self:
            if record.user_id:
                # Define the start and end of the current month
                current_month_start = datetime.today().replace(day=1).strftime('%Y-%m-%d')
                current_month_end = datetime.today().replace(day=1).replace(month=datetime.today().month % 12 + 1, day=1).strftime('%Y-%m-%d')

                # Calculate the start and end of the current week (Monday to Sunday)
                today = datetime.today()
                start_of_week = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')  # Monday of the current week
                end_of_week = (today + timedelta(days=(6 - today.weekday()))).strftime('%Y-%m-%d')  # Sunday of the current week

                # Build search domain based on forecast type
                domain = [
                    "|", "|", "|",
                    ("user_id", "=", record.user_id.id),
                    ("pre_sale_id", "=", record.user_id.id),
                    ("account_manager", "=", record.user_id.id),
                    ("source", "=", record.user_id.id),
                    ("probability", ">=", 70),
                    ("stage_id.name", "not in", ["Won", "Dropped", "Cancelled", "Lost"]),
                ]

                # Adjust date filters based on the forecast type
                if record.forecast_type == "weekly":
                    # Add weekly date filter
                    domain += [("date_deadline", ">=", start_of_week), ("date_deadline", "<=", end_of_week)]
                    _logger.info("Weekly forecast: Filtering leads from %s to %s", start_of_week, end_of_week)
                else:
                    # Add monthly date filter
                    domain += [("date_deadline", ">=", current_month_start), ("date_deadline", "<", current_month_end)]
                    _logger.info("Monthly forecast: Filtering leads from %s to %s", current_month_start, current_month_end)

                # Search leads based on the built domain
                leads = self.env["crm.lead"].search(domain)
                _logger.info("Opportunities found for user %s: %s", record.user_id.name, leads)

                # Sum expected revenue based on the filtered leads
                total_revenue = sum(lead.expected_revenue for lead in leads)

                # Log the total expected revenue based on forecast type
                if record.forecast_type == "weekly":
                    _logger.info(
                        "Total Expected revenue (Weekly) for user %s: %s",
                        record.user_id.name,
                        total_revenue,
                    )
                else:
                    _logger.info(
                        "Total Expected revenue (Monthly) for user %s: %s",
                        record.user_id.name,
                        total_revenue,
                    )

                # Set the computed total expected revenue
                record.total_expected_revenue = total_revenue
                _logger.info("Final Total Expected Revenue for user %s: %s", record.user_id.name, total_revenue)
            else:
                record.total_expected_revenue = 0.0
                _logger.info("No user_id found, setting Total Expected Revenue to 0.")

                
    @api.onchange("forecast_type")
    def _onchange_forecast_type(self):
        self._compute_total_expected_revenue()

    @api.constrains("forecast_amount")
    def _check_forecast_amount(self):
        for record in self:
            if record.forecast_amount > record.total_expected_revenue:
                raise ValidationError(
                    _("Forecast amount cannot be greater than total expected revenue.")
                )

    @api.depends("week_date")
    def _compute_week(self):
        for record in self:
            if record.week_date:
                current_date = fields.Date.from_string(record.week_date)
                year = current_date.year
                month = current_date.month
                month_calculation = calendar.monthcalendar(year, month)
                for week_num, week_days in enumerate(month_calculation, start=1):
                    if current_date.day in week_days:
                        record.week = str(week_num)
                        break
            else:
                record.week = False
