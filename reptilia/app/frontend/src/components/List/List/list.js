/* eslint-disable no-console */
import { API_URL } from "../../../config"
import { bus as EventBus } from "./../../../main"

export default {
    name: "ListForm",
    data() {
        return {
            config: '',
            lists: [],
            campaigns: [],
            columns: [
                {
                    name: 'number',
                    required: true,
                    label: 'N°',
                    align: 'center',
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
                    name: 'campaign',
                    required: true,
                    label: 'CAMPAÑA',
                    align: 'center',
                    field: row => row.campaign,
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
            popupData: {
            },
            showDetails : false,
            pagination:{
                rowsPerPage: 5,
                page: 1,
                sortBy: 'number'
            }
        }
    },
    mounted: function() {
        EventBus.$emit('updateTitle', { title: 'Listas' })
        
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
                            label: campaign.campaign_name,
                            value: campaign.campaign_id
                        }
                    })
                }
                this.refreshLists()
            })
        
        this.$q.screen.setSizes({sm:768})
    },
    methods: {
        getCampaignName(id){
            let response = this.campaigns.filter(campaign => campaign.value == id)
            if(response.length)return response[0].label
            return id
        },
        refreshLists(){
            this.axios.post(`${API_URL}/all-lists`, {}, this.config)
                .then((response)=>{
                    if(response.data.status){
                        this.lists = response.data.lists.map((list, index) => {
                            return {
                                id: list.list_id,
                                number: index + 1,
                                name: list.list_name,
                                campaign: this.getCampaignName(list.campaign_id),
                                status: list.active == 'Y' ? true : false,
                                description: list.list_description,
                            }
                        })
                    }
                })
        },
        onChangeListStatus(id, status){
            status = status ? 'Y' : 'N'
            this.axios.post(`${API_URL}/update-list-status`, {
                list_id: id,
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
        onShowDetails(id){
            let list = this.lists.filter(charge => charge.id == id)
            if(list) this.popupData = list[0]
            this.showDetails = true
        }
    },
}