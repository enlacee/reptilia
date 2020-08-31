/* eslint-disable no-console */
import {API_URL} from './../../../config'
import { bus as EventBus } from "./../../../main"

export default {
    name: "RemoteAgentsList",
    data() {
        return {
            config: {},
            remoteAgents: [],
            campaigns: [],
            columns: [
                {
                    name: 'number',
                    required: true,
                    label: 'N°',
                    align: 'center'
                },
                {
                    name: 'user',
                    required: true,
                    label: 'USUARIO',
                    align: 'center',
                    field: row => row.user,
                },
                {
                    name: 'lines',
                    required: true,
                    label: 'LINES',
                    align: 'center',
                    field: row => row.lines,
                },
                {
                    name: 'campaign_id',
                    required: true,
                    label: 'ID DE CAMPAÑA',
                    align: 'center',
                    field: row => row.campaign_id,
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
            isEditing: {},
            prevLinesValue: null,
            pagination:{
                rowsPerPage: 5,
                page: 1
            },
        }
    },
    mounted: function() {
        EventBus.$emit('updateTitle', { title: 'Agentes remotos' })

        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.axios.post(`${API_URL}/remote-agents-list`, {}, this.config)
        .then(response => {
            if(response.data.status){
                this.remoteAgents = response.data.agents.map(agent => {
                    this.$set(this.isEditing, agent.remote_agent_id, false)
                    return {
                        id: agent.remote_agent_id,
                        user: agent.user_start,
                        lines: agent.number_of_lines,
                        status: agent.status == 'ACTIVE' ? true : false,
                        campaign_id: agent.campaign_id
                    }
                })
            }
        })
        this.$q.screen.setSizes({md: 768})
    },
    methods: {
        onEdit(id, lines){
            this.$set(this.isEditing, id, true)
            this.prevLinesValue = lines
        },
        onSave(id, lines){
            this.axios.post(`${API_URL}/remote-agents-update-lines`, {
                lines, id
            }, this.config).then(response => {
                if(!response.data.status){
                    this.$q.notify({
                        position: 'top',
                        color: 'negative',
                        message: 'Error al actualizar',
                        timeout: 2000,
                    })
                }
            })
            this.prevLinesValue = null
            this.$set(this.isEditing, id, false)
        },
        onCancel(row){
            row.lines = this.prevLinesValue
            this.prevLinesValue = null
            this.$set(this.isEditing, row.id, false)
        }
    }
}