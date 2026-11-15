from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm_with_warning(self):
        self.ensure_one()
        return self.env['order.confirm.warning']._open_for_order(self)

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'form':
            for node in arch.xpath("//button[@name='action_confirm']"):
                node.set('name', 'action_confirm_with_warning')
        return arch, view
