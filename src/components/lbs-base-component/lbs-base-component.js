import hash from 'object-hash'
import Log from '../../lib/lbs.log'
import Bakery from '../../lib/lbs.bakery'

export default class LBSBaseComponet {
    constructor() {
        this.log = new Log()
        this.getComponentId = hashable => hash(hashable)
        this.getCookie = Bakery.getCookie
        this.setCookie = Bakery.setCookie
    }
}
