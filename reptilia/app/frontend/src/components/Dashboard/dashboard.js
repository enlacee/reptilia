/* eslint-disable no-console */
import { ROOT_URL, API_URL } from "./../../config"
import sio from 'socket.io-client'
import { bus as EventBus } from "./../../main"

export default {
    name: "Dashboard",
    data() {
        return {
            calledClients: {
                amount: 0,
                max: 0,
                loading: true
            },
            totalCalls:{
                amount: 0,
                max: 0,
                loading: true
            },
            contactedClients:{
                amount: 0,
                max: 0,
                loading: true
            },
            wrongNumbers: {
                amount: 0,
                max: 0,
                loading: true
            },
            io: null,
            clients: [],
            calls: [],
            date: '',
            prevDate: '',
            locale: {
                days: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
                daysShort: ['Lun', 'Mar', 'Mie','Jue', 'Vie', 'Sab', 'Dom'],
                months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setimebre', 'Octubre', 'Noviembre', 'Diciembre'],
                monthsShort: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']
            },
            dbName: '',
            slowInterval: null,
            fastInterval: null,
            config: {},
            disableFilterDate: true
        }
    },
    mounted: function () {
        EventBus.$emit('updateTitle', { title: 'Dashboard' })
        this.$q.loadingBar.setDefaults({
            size: '0px',
        })
        this.$q.loadingBar.stop()

        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.dbName = localStorage.getItem('entity_prefix')

        let now = new Date()

        this.date = `${now.getDate()}/${('00' + (now.getMonth() + 1)).slice(-2)}/${now.getFullYear()}`
        this.prevDate = this.date

        this.io = sio(`${ROOT_URL}`)
        
        this.io.on('connect', () => {
            this.setInitData()
            this.fastInterval = setInterval(()=>{
                let limit = this.date != this.prevDate ? null : 15
                this.io.emit('update', {key: 'total_calls', db: this.dbName, limit, date: this.date})
            }, 7000)

            this.slowInterval = setInterval(()=>{
                this.io.emit('update', {key: 'called_clients', db: this.dbName, date: this.date})
                this.io.emit('update', {key: 'contacted_clients', db: this.dbName, date: this.date})
                this.io.emit('update', {key: 'wrong_number', db: this.dbName, date: this.date})
            }, 30000)
        })

        this.io.on('update-front', response => {
            if(response.status && this.dateIsNow(this.date)){
                switch(response.key){
                    case 'total_calls':
                        this.joinCalls(response.data.rows, response.limit)
                        break
                    case 'called_clients':
                        this.calledClients.amount = response.data.rows
                        this.calledClients.loading = false
                        break
                    case 'contacted_clients':
                        this.contactedClients.amount = response.data.rows
                        this.contactedClients.loading = false
                        break
                    case 'wrong_number':
                        this.wrongNumbers.amount = response.data.rows
                        this.wrongNumbers.loading = false
                        break
                }
            }
        })
    },
    methods:{
        joinCalls(rows, limit){
            let newData = []
            if(this.calls.length && this.date == this.prevDate){
                let tmp = [...this.calls]
                let r = tmp.splice(-1*limit,limit)
                for(let index in rows){
                    let exist = r.filter(el => el.id == rows[index].id)
                    if(!exist.length){
                        newData.push(rows[index])
                    }
                }
                r = r.concat(newData)
                this.calls = tmp.concat(r).sort((a,b)=>a.id - b.id)
            }else{
                this.calls = rows.sort((a,b)=>a.id - b.id)
            }

            this.totalCalls.amount = this.calls.length
            this.totalCalls.loading = false
        },
        onChangeDate(){
            if(this.date != this.prevDate){
                this.disableFilterDate = true
                this.disconnectSocket()
                this.totalCalls.loading = true
                this.calledClients.loading = true
                this.contactedClients.loading = true
                this.wrongNumbers.loading = true

                this.totalCalls.amount = 0
                this.calledClients.amount = 0
                this.contactedClients.amount = 0
                this.wrongNumbers.amount = 0
                this.calls = 0

                this.prevDate = this.date

                if(this.dateIsNow(this.date)){
                    this.io.open()
                }else{
                    this.setInitData()
                }
            }

            this.$refs.popupProxyRef.hide()
        },
        setInitData(){
            this.axios.post(`${API_URL}/report`, {
                db: this.dbName,
                date: this.date
            }, this.config).then(response => {
                if (response.data.status){
                    this.totalCalls.max = response.data.all_clients * 12
                    this.calledClients.max = response.data.all_clients
                    this.contactedClients.max = response.data.all_clients
                    this.wrongNumbers.max = response.data.all_clients * 2

                    this.calledClients.amount = response.data.called_clients
                    this.contactedClients.amount = response.data.contacted_clients
                    this.wrongNumbers.amount = response.data.wrong_number

                    this.calledClients.loading = false
                    this.contactedClients.loading = false
                    this.wrongNumbers.loading = false

                    this.joinCalls(response.data.total_calls)
                    this.disableFilterDate = false
                }
            })

        },
        disconnectSocket(){
            if(this.io != null) this.io.disconnect()
            if(this.slowInterval != null) clearInterval(this.slowInterval)
            if(this.fastInterval != null) clearInterval(this.fastInterval)
        },
        dateIsNow(date){
            let re = new Date(date.substring(3,5) + '/' + date.substring(0,2) + '/' + date.substring(7,10)).setHours(0,0,0,0)
            let now = new Date().setHours(0,0,0,0)
            return re == now
        }
    },
    beforeDestroy: function() {
        this.disconnectSocket()
        this.$q.loadingBar.setDefaults({
            size: '2px',
        })
    }
}