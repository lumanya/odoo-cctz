{
    'name': 'Birthday Reminder',
    'version': '1.0',
    'summary': 'Send reminder emails to HR for upcoming employee birthdays',
    'description': 'This module sends reminder emails to HR 3 days before an employee’s birthday.',
    'author': 'Your Name',
    'category': 'Human Resources',
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'data/birthday_reminder_cron.xml',
        'data/birthday_reminder_template.xml'
    ],
    'installable': True,
    'application': False,
}
