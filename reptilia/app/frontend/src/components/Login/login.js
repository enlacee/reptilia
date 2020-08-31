/* eslint-disable no-console */
import { API_URL } from "./../../config"

export default {
    name: "Login",
    data() {
        return {
            username: "",
            password: ""
        }
    },
    mounted: function () {

    },
    methods: {
        login() {
            this.axios.post(`${API_URL}/login`, {
                username: this.username,
                password: this.password
            }).then(res => {
                if (res.data.status) {
                    localStorage.setItem('access_token', res.data.access_token)
                    localStorage.setItem('entity_prefix', res.data.entity_prefix)
                    this.$router.push({name:'Dashboard'})
                }else {
                    this.$q.notify({
                        position: 'top',
                        color: 'negative',
                        message: 'Usuario o contraseña incorrectos!',
                        timeout: 2000,
                    })
                }
            })
        },
        enter(){
            if(this.username.length == 0){
                this.$refs.user.focus()
            } else if(this.password.length == 0){
                this.$refs.pass.focus()
            } else {
                this.login()
            }
        }
    }
}
