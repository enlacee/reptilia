/* eslint-disable no-console */
import { API_URL } from "../../config"
import { bus as EventBus } from "./../../main"

export default {
    name: "UserForm",
    data() {
        return {
            submitText : "Agregar",
            rol: '',
            roles: [],
            columns: [
                {
                    name: 'number',
                    label: 'N°',
                    field: 'number',
                    align: 'center'
                },
                {
                    name: 'usuario',
                    label: 'USUARIO',
                    field: 'user',
                    align: 'center'
                },
                {
                    name: 'password',
                    label: 'CONTRASEÑA',
                    field: 'password',
                    align: 'center'
                },
                {
                    name: 'role',
                    label: 'ROL',
                    field: 'role',
                    align: 'center'
                },
                {
                    name: 'actions',
                    label: 'ACCIONES',
                    field: 'actions',
                    align: 'center'
                }
            ],
            data: [],
            config : '',
            isEditing: {
            },
            isNew: false,
            username: '',
            password: '',
            raw_data_users: [],
            pagination:{
                rowsPerPage: 5,
                page: 1
            },
        }
    },
    mounted: function() {
        EventBus.$emit('updateTitle', { title: 'Administrar usuarios' })

        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.axios.post(`${API_URL}/roles`, {}, this.config)
            .then(res => {
                if(res.data.status) {
                    this.roles = res.data.roles.map(item => {
                        return {
                            label: item.role.toUpperCase(),
                            value: item.id,
                        }
                    })
                }
            })
        
        this.refreshUsers()
        this.$q.screen.setSizes({ sm: 768})
    },
    methods: {
        refreshUsers(){
            this.axios.post(`${API_URL}/users`, {}, this.config)
            .then(res => {
                if(res.data.status) {
                    this.raw_data_users = res.data.users
                    this.data = res.data.users.map((item, index) => {
                        return {
                            id: item.id,
                            number: index + 1,
                            user: item.username,
                            password: item.password,
                            role: item.role.toUpperCase()
                        }
                    })
                }
            })
        },
        actionUser() {
            if(!this.isEditing){
                this.axios.post(`${API_URL}/register`, {
                    username: this.username,
                    password: this.password,
                    role_id: this.rol.value,
                }, this.config)
                .then(res => {
                    if(res.data.status) {
                        this.refreshUsers()
                        this.$q.notify({
                            position: 'top',
                            color: 'positive',
                            message: 'Usuario agregado',
                            timeout: 2000,
                        })
                        this.username = ''
                        this.password = ''
                        this.rol = ''
                        this.isNew = false
                    }else{
                        this.$q.notify({
                            position: 'top',
                            color: 'negative',
                            message: 'Corrija el formulario',
                            timeout: 2000,
                        })
                    }
                })
            }
        },
        actionEdit(id){
            // let obj = this.raw_data_users.filter(item =>{
            //     return item.id == id
            // })

            // if(obj.length){
            //     this.isEditing = true
            //     this.submitText = "Editar"
            //     this.username = obj[0].username
            //     this.rol = {
            //         label: obj[0].role.toUpperCase(),
            //         value: obj[0].role_id
            //     }
            // }
            this.$set(this.isEditing, id, true)
        }
    }
}