/* eslint-disable no-console */
import { API_URL } from "../../../config"
import { bus as EventBus } from "./../../../main"

export default {
    name: "FormCampaign",
    data() {
        return {
            id: "",
            name: "",
            campaignIds: [],
            config: {}
        }
    },
    mounted: function() {
        EventBus.$emit('updateTitle', { title: 'Crear Campaña' })
        
        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.axios.post(`${API_URL}/campaigns`, {}, this.config).then(res => {
            if (res.data.status) {
                this.campaignIds = res.data.campaigns.map(item => {
                    return String(item.campaign_id)
                })
            }
        })
    },
    methods: {
        validateSuccess(){
            if(this.id > 99 && !this.campaignIds.includes(this.id)) return true
            return false
        },
        save() {
            if(this.validateSuccess()){
                this.axios.post(`${API_URL}/create-campaign`, {
                    campaign_name: this.name,
                    campaign_id: this.id
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
                        this.$refs.campaignId.resetValidation()
                        this.$refs.campaignName.resetValidation()
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