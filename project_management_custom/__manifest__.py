{
    'name': 'Project management Custom',
    'version': '1.0',
    'summary': 'Customization of the Project Kanban view',
    'author': 'Ebenezeri',
    'category': 'Project',
    'depends': ['project'],  # Ensure 'project' is installed
    'data': [
        'views/project_management_view.xml',
    ],
    'installable': True,
    'application': False,
}
