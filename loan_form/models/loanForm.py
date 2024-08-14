from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request
from werkzeug.urls import url_encode  # type: ignore
import logging

_logger = logging.getLogger(__name__)


class loanform(models.Model):
    _name = "loan.form"
    _inherit = "mail.thread"
    _description = "A loan Form"
    _order = "loan_form_number desc, id desc"

    b_state = fields.Selection(
        [
            ("on", "on"),
            ("off", "off"),
        ],
        default="off",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("second_approval", "Second Approval"),
            ("third_approval", "Third Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        track_visibility="onchange",
        tracking=True,
    )

    active = fields.Boolean(default=True, readonly=True)

    loan_amount = fields.Integer(string="Loan amount", required=True)
    repayment_months = fields.Selection(
        string="Repayment months",
        selection=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("6", "6"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
            ("11", "11"),
            ("12", "12"),
        ],
        default="1",
    )
    reason = fields.Text(string="Reason", required=True)
    constant = fields.Float(default=0.01)
    constant1 = fields.Float(default=0.005)

    service_charge = fields.Float(
        string="service charge", compute="_calculate_service_charge"
    )
    subtotal = fields.Float(string="subtotal", compute="_calculate_subtotal")
    monthly_rate = fields.Float(
        string="Monthly Rate", compute="_calculate_monthly_rate"
    )
    monthly_interest = fields.Float(
        string="Monthly Interest", compute="_calculate_monthly_interest"
    )
    total_loan = fields.Float(string="Total Loan", compute="_calculate_Total")

    loan_form_number = fields.Char(
        string="Loan Form Number",
        copy=False,
        readonly=True,
        required=True,
        default=lambda self: _("New"),
    )

    attachment_ids = fields.One2many("ir.attachment", "res_id", string="Attachments")

    supported_attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attach File",
        compute="_compute_supported_attachment_ids",
        inverse="_inverse_supported_attachment_ids",
    )
    supported_attachment_ids_count = fields.Integer(
        compute="_compute_supported_attachment_ids"
    )

    repayment_schedule = fields.Float(
        string="Avarage Monthly Return", compute="_compute_repayment_schedule"
    )

    _rec_name = "loan_form_number"

    user_id = fields.Many2one(
        "res.users",
        string="Loan Requester",
        compute="_compute_user",
        store=True,
        readonly=True,
    )

    loan_officer_id = fields.Many2one(
        "res.users", string="Loan officer", compute="_compute_loan_officer", store=True
    )

    employee_id = fields.Many2one(
        "hr.employee", string="Employee", compute="_compute_employee", required=True
    )

    employee_nida_number = fields.Char(
        string='Employee Identification Number',
        related='employee_id.identification_id',
        store=True,
    )

    parent_identification_number = fields.Char(
        string=' Manager Identification Number',
        related='employee_id.parent_id.identification_id',
        store=True,
    )

    # private_street = fields.Char(
    #     string='Private Address',
    #     related='employee_id.private_street',
    #     store=True,
    # )

    loan_officer_name = fields.Char(
        string=' Loan Officer',
        related='employee_id.parent_id.loan_officer_id.name',
        store=True,
    )

    loan_officer_department = fields.Char(
        string=' Loan Officer Department',
        related='employee_id.loan_officer_id.department_id.name',
        store=True,
    )

    loan_officer_address = fields.Char(
        string=' Loan Officer Address',
        related='employee_id.loan_officer_id.address_id.name',
        store=True,
    )


    @api.depends("user_id")
    def _compute_loan_officer(self):
        self.loan_officer_id = self.env.user.employee_id.loan_officer_id

    @api.depends("create_uid")
    def _compute_user(self):
        for record in self:
            record.user_id = record.create_uid

    @api.depends("user_id")
    def _compute_employee(self):
        for record in self:
            employee = self.env["hr.employee"].search(
                [("user_id", "=", record.user_id.id)], limit=1
            )
            record.employee_id = employee.id

    @api.model
    def create(self, vals):
        vals["b_state"] = "on"
        if vals.get("loan_form_number", _("New")) == _("New"):
            vals["loan_form_number"] = self.env["ir.sequence"].next_by_code(
                "loan.number"
            ) or _("New")
        res = super(loanform, self).create(vals)
        res._check_loan_amount()
        return res

    @api.constrains("loan_amount")
    def _check_loan_amount(self):
        for record in self:
            if record.loan_amount == 0:
                raise UserError("Loan amount must not be zero")

    @api.depends("attachment_ids")
    def _compute_supported_attachment_ids(self):
        for record in self:
            record.supported_attachment_ids = record.attachment_ids
            record.supported_attachment_ids_count = len(record.attachment_ids.ids)

    def _inverse_supported_attachment_ids(self):
        for record in self:
            record.attachment_ids = record.supported_attachment_ids

    @api.depends("loan_amount", "constant")
    def _calculate_service_charge(self):
        for record in self:
            record.service_charge = record.loan_amount * record.constant

    @api.depends("loan_amount", "service_charge")
    def _calculate_subtotal(self):
        for record in self:
            record.subtotal = record.loan_amount + record.service_charge

    @api.depends("constant1", "repayment_months")
    def _calculate_monthly_rate(self):
        for record in self:
            record.monthly_rate = record.constant1 * int(record.repayment_months)

    @api.depends("monthly_rate", "subtotal")
    def _calculate_monthly_interest(self):
        for record in self:
            record.monthly_interest = record.monthly_rate * record.subtotal

    @api.depends("subtotal", "monthly_interest")
    def _calculate_Total(self):
        for record in self:
            record.total_loan = record.subtotal + record.monthly_interest

    @api.depends("total_loan", "repayment_months")
    def _compute_repayment_schedule(self):
        for record in self:
            record.repayment_schedule = record.total_loan / int(record.repayment_months)

    def action_submit(self):
        if self.env.user.employee_id and self.env.user.employee_id.loan_officer_id:
            group_officer1 = self.env.ref("loan_form.group_loan_officer")
            group_officer1.sudo().write(
                {"users": [(4, self.env.user.employee_id.loan_officer_id.id)]}
            )

            accountant = self.env["hr.employee"].search(
                [("job_title", "=", "Head of Procurement & Accountant")], limit=1
            )
            accountant_group = self.env.ref("loan_form.group_loan_manager")
            accountant_group.sudo().write({"users": [(4, accountant.user_id.id)]})

            manager = self.env["hr.employee"].search(
                [("job_title", "=", "General Manager")], limit=1
            )
            manager_group = self.env.ref("loan_form.group_loan_admin")
            manager_group.sudo().write({"users": [(4, manager.user_id.id)]})
            self.state = "to_approve"
            self.send_email_to_loan_officer()
        else:
            raise UserError(
                "Please contact your Administrator to set your Loan Officer."
            )

    def action_approve(self):
        self.state = "second_approval"
        self.action_send_email()
        self.send_email_to_accountant()

    def action_reject(self):
        self.state = "rejected"
        self.action_send_email()

    def action_approve1(self):
        self.state = "third_approval"
        self.action_send_email()
        self.send_email_to_general_manager()

    def action_reject1(self):
        self.state = "rejected"
        self.action_send_email()

    def action_approve2(self):
        self.state = "approved"
        self.action_send_email()

    def action_reject2(self):
        self.state = "rejected"
        self.action_send_email()

    menu_id = fields.Integer(string="Menu ID")
    action_id = fields.Integer(string="Action ID")

    @api.model
    def generate_link(self, menu_id, action_id):

        base_url = request.httprequest.url_root

        # Find menu_id based on the menu name
        menu = self.env["ir.ui.menu"].search([("name", "=", "Loan Request")])
        menu_id = menu.id if menu else False

        # Find action_id based on the action name
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            .search([("name", "=", "Loan View")])
        )
        action_id = action.id if action else False

        if menu_id and action_id:
            params = {"menu_id": menu_id, "action": action_id}
            if (
                hasattr(self, "_origin") and self._origin
            ):  # Check if called within a record context
                params["id"] = (
                    self._origin.id
                )  # Automatically include current record ID

                # Find the view ID associated with the current record
                view_id = self._origin.get_formview_id()
                if view_id:
                    params["view_type"] = "form"
                    params["view_id"] = view_id
                print(f"***** Base Url {base_url}")

            return base_url + "web#" + url_encode(params)
        else:
            # Handle the case where either menu or action is not found
            return False

    def _get_my_records(self):
        return self.search([("create_uid", "=", self.env.uid)])

    # sending email
    def action_send_email(self):
        template = self.env.ref("loan_form.email_loan_approval_status")
        for rec in self:
            template.send_mail(rec.id, force_send=True)

    def _get_loan_officer_emails(self):
        users = self.env.user.employee_id.loan_officer_id
        return [user for user in users if user.email]

    def send_email_to_loan_officer(self):
        users = self.env.user.employee_id.loan_officer_id
        template = self.env.ref("loan_form.email_template_loan_officer_approver")

        if template and users:
            for user in users:
                if user.email:
                    template.with_context(user=user).send_mail(
                        self.id, force_send=True, email_values={"email_to": user.email}
                    )
                    _logger.info("Email sent to %s (%s)" % (user.name, user.email))
                else:
                    _logger.warning(
                        "User %s does not have an email address." % user.name
                    )
        else:
            if not template:
                _logger.warning(
                    "Email template 'email_template_loan_officer_approver' not found."
                )
            if not users:
                _logger.warning("No users found in the 'Loan Officers' group.")

    def _get_accountant_emails(self):
        accountant = self.env["hr.employee"].search(
            [("job_title", "=", "Head of Procurement & Accountant")], limit=1
        )
        return accountant

    def send_email_to_accountant(self):

        accountant = self.env["hr.employee"].search(
            [("job_title", "=", "Head of Procurement & Accountant")], limit=1
        )
        template = self.env.ref("loan_form.email_template_accountant_approver")

        if template and accountant:
            if accountant.work_email:
                template.send_mail(
                    self.id,
                    force_send=True,
                    email_values={"email_to": accountant.work_email},
                )
                _logger.info(
                    "Email sent to %s (%s)" % (accountant.name, accountant.work_email)
                )
            else:
                _logger.warning(
                    "User %s does not have an email address." % accountant.name
                )
        else:
            if not template:
                _logger.warning(
                    "Email template 'email_template_accountant_approver' not found."
                )
            if not accountant:
                _logger.warning("No users found in the 'Accountant'")

    def _get_general_manager_emails(self):
        manager = self.env["hr.employee"].search(
            [("job_title", "=", "General Manager")], limit=1
        )
        return manager

    def send_email_to_general_manager(self):
        manager = self.env["hr.employee"].search(
            [("job_title", "=", "General Manager")], limit=1
        )
        template = self.env.ref("loan_form.email_template_general_manager_approver")

        if template and manager:
            if manager.work_email:
                template.send_mail(
                    self.id,
                    force_send=True,
                    email_values={"email_to": manager.work_email},
                )
                _logger.info(
                    "Email sent to %s (%s)" % (manager.name, manager.work_email)
                )
            else:
                _logger.warning(
                    "User %s does not have an email address." % manager.name
                )
        else:
            if not template:
                _logger.warning(
                    "Email template 'email_template_general_manager_approver' not found."
                )
            if not manager:
                _logger.warning("No users found in the 'manager'")
