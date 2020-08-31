/* eslint-disable no-console */
import { API_URL } from "../../../config"
import { bus as EventBus } from "./../../../main"

export default {
    name: "CampaignList",
    data() {
        return {
            config: {},
            campaigns: [],
            columns: [
                {
                    name: 'number',
                    required: true,
                    label: 'N°',
                    align: 'center',
                    field: row => row.name,
                },
                {
                    name: 'name',
                    required: true,
                    label: 'NOMBRE',
                    align: 'center',
                    field: row => row.name,
                },
                {
                    name: 'id',
                    required: true,
                    label: 'ID',
                    align: 'center',
                    field: row => row.id,
                },
                {
                    name: 'status',
                    required: true,
                    label: 'ESTADO',
                    align: 'center',
                    field: row => row.status,
                },
                {
                    name: 'actions',
                    required: true,
                    label: 'ACCIONES',
                    align: 'center'
                }
            ],
            popupData: {},
            showDetails : false,
            pagination:{
                rowsPerPage: 5,
                page: 1,
            }
        }
    },
    mounted: function() {
        EventBus.$emit('updateTitle', { title: 'Campañas' })
        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.axios.post(`${API_URL}/campaigns`, {}, this.config)
            .then((response)=>{
                if(response.data.status){
                    this.campaigns = response.data.campaigns.map(campaign => {
                        return {
                            id: campaign.campaign_id,
                            name: campaign.campaign_name,
                            status: campaign.active == 'Y' ? true : false,
                        }
                    })
                }
            })
        
        this.$q.screen.setSizes({sm: 768})
    },
    methods: {
        onShowDetails(id){
            let campaign = this.campaigns.filter(campaign => campaign.id == id)
            if(campaign) this.popupData = campaign[0]
            this.showDetails = true
        },
        onChangeStatus(id, status){
            status = status ? 'Y' : 'N'
            this.axios.post(`${API_URL}/update-campaign-status`, {
                campaign_id: id,
                status
            }, this.config)
            .then((response)=>{
                if(!response.data.status){
                    this.$q.notify({
                        position: 'top',
                        color: 'negative',
                        message: 'Error al actualizar',
                        timeout: 2500,
                        actions: [{ icon: 'close', color: 'white' }]
                    })
                }
            })
        },
    },
}