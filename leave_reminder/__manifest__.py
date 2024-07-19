{
    'name': 'Leave Approval Reminder',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Send reminder emails for pending leave approvals',
    'depends': ['hr_holidays', 'mail'],
    'data': [
        'data/leave_reminder_cron.xml',
        'data/leave_remainder_template.xml'
    ],
    'installable': True,
    'application': False,
}
