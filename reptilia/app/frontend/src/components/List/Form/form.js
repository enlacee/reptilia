/* eslint-disable no-console */
import { API_URL } from "../../../config"
import { bus as EventBus } from "./../../../main"

export default {
    name: "FormList",
    data() {
        return {
            id: "",
            name: "",
            campaigns: [],
            campaign: '',
            listIds: [],
            config: {}
        }
    },
    mounted: function() {
        EventBus.$emit('updateTitle', { title: 'Crear lista' })

        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.axios.post(`${API_URL}/campaigns`, {}, this.config).then(res => {
            if (res.data.status) {
                this.campaigns = res.data.campaigns.map(item => {
                    return {
                        label: item.campaign_name,
                        value: item.campaign_id
                    }
                })
            }
        })

        this.axios.post(`${API_URL}/lists`, {}, this.config).then(res => {
            if (res.data.status) {
                this.listIds = res.data.lists.map(item => {
                    return String(item.list_id)
                })
            }
        })
    },
    methods: {
        validateSuccess(){
            if(this.id > 99 && !this.listIds.includes(this.id) && this.campaign.value != undefined) return true
            return false
        },
        save() {
            if(this.validateSuccess()){
                this.axios.post(`${API_URL}/create-list`, {
                    list_id: this.id,
                    list_name: this.name,
                    campaign_id: this.campaign.value
                }, this.config).then(res => {
                    if (res.data.status) {
                        this.$q.notify({
                            position: 'top',
                            color: 'positive',
                            message: 'Se creó la lista!',
                            timeout: 2000,
                        })

                        this.id = ''
                        this.name = ''
                        this.campaign = {}

                        setTimeout(()=>{
                            this.$refs.listid.resetValidation()
                            this.$refs.listname.resetValidation()
                            this.$refs.listcampaign.resetValidation()
                        }, 10)

                    } else {
                        this.$q.notify({
                            position: 'top',
                            color: 'negative',
                            message: 'Error! Verifique los datos',
                            timeout: 2500,
                            actions: [{ icon: 'close', color: 'white' }]
                        })
                    }
                })
            } else {
                this.$q.notify({
                    position: 'top',
                    color: 'warning',
                    message: 'Complete los campos',
                    timeout: 2500,
                    actions: [{ icon: 'close', color: 'white' }]
                })
            }
        }
    }
}
