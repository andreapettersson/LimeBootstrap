import ko from 'knockout'
import limeMenuTemplate from './lbs-menu.tpl.html'
import LBSBaseComponent from '../lbs-base-component/lbs-base-component'

class LBSMenuVM extends LBSBaseComponent {
    constructor(params) {
        super()
        const {
            title = '',
        } = params
        this.title = title
        this.id = this.getComponentId(this)
        this.expanded = ko.observable(this.getCookie(`${this.id}_expanded`) === 'true')
    }

    toggle() {
        this.expanded(!this.expanded())
        this.setCookie(`${this.id}_expanded`, this.expanded())
    }
}

ko.components.register('lbs-menu', { viewModel: LBSMenuVM, template: limeMenuTemplate })
