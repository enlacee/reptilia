/* eslint-disable no-console */
import { API_URL } from "./../../../config"
import { bus as EventBus } from "./../../../main"

export default {
    name: "DashboardLayout",
    data() {
        return {
            drawer: false,
            ifAbove: false,
            headerState: true,
            config: '',
            miniDrawState: true,
            actives: {},
            title: 'Dashboard',
            prevSelected: '',
            entity: '',
            entities: [],
            modules: []
        }
    },
    mounted: function () {
        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.axios.post(`${API_URL}/get-modules`, {}, this.config)
            .then(res => {
                this.modules = res.data.modules
                let module = this.$router.currentRoute.meta.module
                let row = this.modules.filter(m => m.route_name == module)
                if(row.length) {
                    this.route(module, row[0].id, false)
                    this.ifAbove = true
                }
            })

        this.axios.post(`${API_URL}/entities-user`, {}, this.config)
            .then(res => {
                res.data.entities.forEach(element => {
                    if (element.prefix === localStorage.getItem('entity_prefix')) {
                        this.entity = element.name
                    }
                })
                this.entities = res.data.entities.map(v => {
                    return {
                        label: v.name,
                        value: v.id,
                        prefix: v.prefix
                    }
                })
            })

        EventBus.$on('updateTitle', data => {
            this.title = data.title
        })
    },
    methods: {
        logout() {
            this.axios.post(`${API_URL}/logout`, {}, this.config)
            .then(res => {
                if(res.data.status) {
                    this.$q.notify({
                        position: 'top',
                        color: 'blue-grey-7',
                        message: 'Se cerró la sesión',
                        timeout: 2000,
                    })
                }
            })

            localStorage.removeItem('access_token')
            localStorage.removeItem('entity_prefix')

            this.$router.push({name:'Login'})
        },
        route(name, moduleId, push = true) {
            if(this.prevSelected != undefined) this.actives[this.prevSelected] = false
            this.actives[moduleId] = true
            this.prevSelected = moduleId
            if(push)this.$router.push({name})
        },
        updateEntity(entity){
            localStorage.setItem('entity_prefix', entity.prefix)
        },
        newTab(name){
            let routeData = this.$router.resolve({name})
            window.open(routeData.href, '_blank')
        }
    }
}
