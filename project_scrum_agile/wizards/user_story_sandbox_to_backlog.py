# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SandboxTransferToBacklog(models.TransientModel):
    _name = 'project.scrum.sandbox.to.backlog'
    _description = 'Transfer user story from sandbox to Product Backlogs'

    role_id = fields.Many2one('project.scrum.role', "As")
    name = fields.Char('I want', size=128)
    for_then = fields.Char('For', size=128)
    project_id = fields.Many2one(
        'project.project',
        "Project",
        domain=[('is_scrum', '=', True)]
    )
    developer_id = fields.Many2one('res.users', 'Developer')
    release_id = fields.Many2one('project.scrum.release', "Release")

    @api.model
    def default_get(self, fields):
        res = super(SandboxTransferToBacklog, self).default_get(fields)
        sandboxes = self.env['project.scrum.sandbox'].browse(
            self._context['active_id'])
        res.update({
            'project_id': sandboxes.project_id.id
        })
        return res

    def do_transfer(self):
        """ Transfer user story from sandbox to Product Backlogs
        @param self: The object pointer
        """
        context = self._context or {}
        backlog_obj = self.env['project.scrum.product.backlog']
        sandboxes = self.env['project.scrum.sandbox'].browse(
            context['active_ids'])
        for sandbox in sandboxes:
            vals = {
                'role_id': sandbox.role_id.id,
                'name': sandbox.name,
                'for_then': sandbox.for_then,
                'project_id': sandbox.project_id.id,
                'user_id': sandbox.developer_id.id,
                'release_id': self.release_id and self.release_id.id or False,
                'description': sandbox.name,
            }
            context = dict(context)
            context['default_project_id'] = sandbox.project_id.id
            backlog_id = backlog_obj.with_context(context).create(vals)
            if backlog_id:
                sandbox.unlink()
        return True
