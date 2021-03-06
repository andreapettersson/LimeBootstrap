import { NotYetImplementedError } from '../lbs.errors'

/**
 *
 * @interface
 * @mixin
 * @export
 * @class DataSource
 */
export default class DataSource {
    constructor({
        type, source, alias = '', protocol = 'https',
    }, session, server, database) {
        this.type = type
        this.source = source
        this.alias = alias
        this.protocol = protocol
        this.session = session
        this.serverURLComponent = encodeURI(server)
        this.databaseURLComponent = encodeURI(database)
        this.protocol = protocol
    }

    get serverURL() {
        return `${this.protocol}://${this.serverURLComponent}/${this.databaseURLComponent}`
    }

    /**
     *
     * @private
     * @param {string} [url='']
     * @param {*} [settings={}]
     * @returns
     * @memberof DataSource
     */
    async _fetch(url = '', settings = {}) {
        const { method = 'GET' } = settings
        const _settings = {
            mode: 'cors',
            headers: { sessionid: this.session },
        }
        try {
            const response = await fetch(url, { ...settings, ..._settings })
            return response
        } catch (e) {
            lbs.log.info(`Using VBA fallback method for data source ${this.type}`)
            const payload = settings.body ? `, ${btoa(settings.body)}` : ''
            return {
                json: async () => JSON.parse(lbs.common.executeVba(`LBSHelper.CRMEndpoint, ${url}, ${method}${payload}`)),
                status: 'Fetched through VBA... No idea',
            }
        }
    }



    /**
     * Should return a promise to the data from the datasource
     * @async
     * @static
     * @abstract
     * @memberof DataSource
     * @returns {Promise<object>}
     */
    static async fetch() {
        throw new NotYetImplementedError('Should be implemented by subclass')
    }
}
