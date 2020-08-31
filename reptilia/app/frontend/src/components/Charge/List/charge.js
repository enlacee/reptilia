/* eslint-disable no-console */
import { API_URL } from "../../../config"
import { bus as EventBus } from "./../../../main"

export default {
    name: "Charge",
    data() {
        return {
            config: '',
            charges: [],
            carriers: [],
            carrier: {},
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
                    name: 'entity',
                    required: true,
                    label: 'ENTIDAD',
                    align: 'center',
                    field: row => row.entity,
                },
                {
                    name: 'camp',
                    required: true,
                    label: 'CAMPAÑA',
                    align: 'center',
                    field: row => row.camp,
                },
                {
                    name: 'lista',
                    required: true,
                    label: 'LISTA',
                    align: 'center',
                    field: row => row.list,
                },
                {
                    name: 'carrier',
                    required: true,
                    label: 'PROVEEDOR',
                    align: 'center',
                    field: row => row.carrier,
                },
                {
                    name: 'actions',
                    required: true,
                    label: 'ACCIONES',
                    align: 'center'
                }
            ],
            pagination:{
                rowsPerPage: 7,
                page: 1
            },
            popupData: {
                entity: '',
                camp: '',
                list: '',
                proveedor: '',
                iterations: '',
                seconds: ''
            },
            showDetails : false
        }
    },
    mounted: function() {
        EventBus.$emit('updateTitle', { title: 'Cargas' })

        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.axios.post(`${API_URL}/carriers`, {}, this.config)
            .then((response)=>{
                if(response.data.status){
                    this.carriers = response.data.carriers.map(carrier => {
                        return {
                            label: carrier.name,
                            value: carrier.id
                        }
                    })
                }
            })

        this.axios.post(`${API_URL}/all-lists`, {}, this.config)
            .then((response)=>{
                if(response.data.status){
                    this.lists = response.data.lists.map(list => {
                        return {
                            label: list.list_name,
                            value: list.list_id
                        }
                    })
                }
            })

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
                this.refreshCharges()
            })
        this.$q.screen.setSizes({md: 900})
    },
    methods: {
        getCampaignName(id){
            let response = this.campaigns.filter(campaign => campaign.value == id)
            if(response.length)return response[0].label
            return id
        },
        getListName(id){
            let response = this.lists.filter(list => list.value == id)
            if(response.length)return response[0].label
            return id
        },
        refreshCharges(){
            this.axios.post(`${API_URL}/all-charges`, {}, this.config)
                .then((response)=>{
                    if(response.data.status){
                        let carrier_list = {}
                        this.charges = response.data.charges.map((charge) => {
                            this.$set(carrier_list, charge.charge_id, {
                                label: charge.carrier_name,
                                values: charge.carrier_id
                            })
                            return {
                                id: charge.charge_id,
                                entity: charge.entity_name,
                                camp: this.getCampaignName(charge.campaign_id),
                                list: this.getListName(charge.list_id),
                                carrier: charge.carrier_name,
                                iterations: charge.iterations,
                                seconds: charge.seconds_between_iterations,
                                created: new Date(charge.created_at).toLocaleString(),
                                updated: new Date(charge.created_at).toLocaleString()
                            }
                        }).sort((a, b) => b.id - a.id)
                        this.carrier = carrier_list
                    }
                })
        },
        onChangeCarrier(charge_id, carrier){
            this.axios.post(`${API_URL}/update-charge`, {
                charge_id : charge_id,
                carrier_id : carrier.value
            }, this.config)
            .then((response)=>{
                if(!response.data.status){
                    this.$q.notify({
                        position: 'top',
                        color: 'negative',
                        message: 'Error al actualizar',
                        timeout: 2000,
                    })
                }
            })
        },
        onShowDetails(id){
            let charge = this.charges.filter(charge => charge.id == id)
            if(charge) this.popupData = charge[0]
            this.showDetails = true
        }
    },
}
