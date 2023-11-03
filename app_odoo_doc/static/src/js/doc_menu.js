/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import {registry} from '@web/core/registry';
import {useService} from '@web/core/utils/hooks';
import {Component, onWillStart} from '@odoo/owl';


export class DocMenu extends Component {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.actionService = useService('action');
    }

    async actionOpenDoc() {
        const action = this.actionService.currentController.action;
        const res_action = await this.orm.call("ir.module.module", "action_xml_go_doc",[], {
            xml_id: action.xml_id,
        });
        this.actionService.doAction(res_action);

    }

}

DocMenu.template = 'app_odoo_doc.DocMenu';


export const DocSystrayItem = {
    Component: DocMenu,
};

registry.category('systray').add('DocMenu', DocSystrayItem, {sequence: 1});
