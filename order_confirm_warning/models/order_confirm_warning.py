from markupsafe import Markup

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_amount

ALLOWED_MODELS = {
    'sale.order': 'action_confirm',
    'purchase.order': 'button_confirm',
}


class OrderConfirmWarning(models.TransientModel):
    _name = 'order.confirm.warning'
    _description = 'Order Confirmation Warning'

    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    summary = fields.Html(readonly=True, sanitize=False)

    @api.model
    def _open_for_order(self, order):
        """Build the summary and return the popup action."""
        order.ensure_one()
        is_po = order._name == 'purchase.order'
        qty_field = 'product_qty' if is_po else 'product_uom_qty'
        currency = order.currency_id
        lines = order.order_line.filtered(lambda l: not l.display_type)
        total_qty = sum(lines.mapped(qty_field))

        rows = Markup('').join(
            Markup(
                '<tr><td>%s</td><td class="text-end">%s</td>'
                '<td class="text-end">%s</td><td class="text-end">%s</td></tr>'
            ) % (
                line.product_id.display_name or line.name or '',
                '%g' % line[qty_field],
                format_amount(self.env, line.price_unit, currency),
                format_amount(self.env, line.price_subtotal, currency),
            )
            for line in lines
        )

        summary = (
            Markup('<div class="alert alert-warning" role="alert"><strong>%s</strong></div>')
            % _("Please review the number of items, quantities and prices before confirming.")
        ) + (
            Markup('<p>%s: <strong>%s</strong> &nbsp;|&nbsp; %s: <strong>%s</strong></p>')
            % (_("Items"), len(lines), _("Total quantity"), '%g' % total_qty)
        ) + (
            Markup(
                '<table class="table table-sm"><thead><tr>'
                '<th>%s</th><th class="text-end">%s</th>'
                '<th class="text-end">%s</th><th class="text-end">%s</th>'
                '</tr></thead><tbody>%s</tbody></table>'
            ) % (_("Product"), _("Quantity"), _("Unit Price"), _("Subtotal"), rows)
        ) + (
            Markup('<p class="fs-4 text-end"><strong>%s: %s</strong></p>')
            % (_("Total"), format_amount(self.env, order.amount_total, currency))
        )

        wizard = self.create({
            'res_model': order._name,
            'res_id': order.id,
            'summary': summary,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _("Confirm Purchase Order") if is_po else _("Confirm Sales Order"),
            'res_model': self._name,
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                k: v for k, v in order.env.context.items()
                if k == 'validate_analytic'
            },
        }

    def action_confirm_order(self):
        self.ensure_one()
        method = ALLOWED_MODELS.get(self.res_model)
        if not method:
            raise UserError(_("Unsupported document type."))
        order = self.env[self.res_model].browse(self.res_id).exists()
        if not order:
            return {'type': 'ir.actions.act_window_close'}
        result = getattr(order, method)()
        if isinstance(result, dict):
            return result
        return {'type': 'ir.actions.act_window_close'}
