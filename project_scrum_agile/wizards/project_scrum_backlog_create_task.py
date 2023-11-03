# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class BacklogCreateTask(models.TransientModel):
    _name = 'project.scrum.backlog.create.task'
    _description = 'Create Tasks from Product Backlogs'

    user_id = fields.Many2one(
        'res.users',
        'Assign To',
        help="Responsible user who can work on task"
    )

    def do_create(self):
        """ Create Tasks from Product Backlogs
        @param self: The object pointer
        """
        context = self._context or {}
        task = self.env['project.task']
        backlog_id = self.env['project.scrum.product.backlog']
        document_obj = self.env['ir.attachment']
        ids_task = []
        backlogs = backlog_id.browse(context['active_ids'])
        # search_view_ref = self.env.ref('project.view_task_search_form', False)
        for backlog in backlogs:
            task_id = task.create({
                'product_backlog_id': backlog.id,
                'name': backlog.name,
                'description': backlog.description,
                'project_id': backlog.project_id.id,
                'user_ids': [(6,0,self.user_id.ids)] or False,#self.user_id and self.user_id.id
                'planned_hours': backlog.expected_hours,
                'remaining_hours': backlog.expected_hours,
                'sequence': backlog.sequence,
            })
            document_ids = document_obj.search(
                [('res_id', '=', backlog.id),
                 ('res_model', '=', backlog_id._name)])
            for document_id in document_ids:
                document_id.copy(default={'res_id': task_id.id,
                                          'res_model': task._name})
            ids_task.append(task_id.id)
        # Create action.
        action = {
            'name': _('Tasks'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
        }
        if len(ids_task) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': ids_task[0],
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', ids_task)],
            })
        return action
