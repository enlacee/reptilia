/* eslint-disable no-console */
import { API_URL } from "./../../../config"
import XLSX from 'xlsx'
import { bus as EventBus } from "./../../../main"

export default {
    name: "ChargeForm",
    data() {
        return {
            msg: "",
            isError: false,
            iterations: 0,
            seconds: 0,
            loading: false,
            btnMatchLoad: false,
            lists: [],
            carriers: [],
            channels: [],
            carrier: '',
            list: '',
            channel: '',
            dialogStatus: false,
            config: '',
            dbName: '',
            report: {
                msg: 'NA',
                time: 'NA',
                clients: 'NA',
                products: 'NA',
                duplicates: 'NA',
                out: 'NA',
                process: 'NA',
                show: false
            },
            isReport: false,
            excelColumns: [],
            dataColumn: {
                code: {
                    field: '',
                    class: 'grey',
                    clickClass: 'blue-grey-10'
                },
                name: {
                    field: '',
                    class: 'grey',
                    clickClass: 'red'
                },
                product: {
                    field: '',
                    class: 'grey',
                    clickClass: 'orange-9'
                },
                amount: {
                    field: '',
                    class: 'grey',
                    clickClass: 'brown-8'
                },
                currency: {
                    field: '',
                    class: 'grey',
                    clickClass: 'blue-8'
                },
                date: {
                    field: '',
                    class: 'grey',
                    clickClass: 'green-8'
                },
                phone: {
                    field: '',
                    class: 'grey',
                    clickClass: 'secondary'
                },
                prevSelected: ''
            },
            dataColMatch: {},
            allowMatch: false,
            chargeLoadedClass: 'grey'
        }
    },
    mounted: function() {
        EventBus.$emit('updateTitle', { title: 'Realizar carga' })

        this.config = {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')
            }
        }

        this.dbName = localStorage.getItem('entity_prefix')

        this.axios.post(`${API_URL}/lists`, {}, this.config).then(res => {
            if (res.data.status) {
                this.lists = res.data.lists.map(item => {
                    return {
                        label: item.list_name,
                        value: item.list_id
                    }
                })
            }
        })

        this.axios.post(`${API_URL}/carriers`, {entity_prefix: this.dbName}, this.config).then(res => {
            if (res.data.status) {
                this.carriers = res.data.carriers.map(item => {
                    return {
                        label: item.name,
                        value: item.id
                    }
                })
            }
        })

        this.axios.post(`${API_URL}/channels`, {}, this.config).then(res => {
            if (res.data.status) {
                this.channels = res.data.channels.map(item => {
                    return {
                        label: item.name.toUpperCase(),
                        value: item.id
                    }
                })
                let _default = this.channels.filter(item => item.label == 'CALL')
                if(_default.length) this.channel = _default[0]
            }
        })

    },
    methods: {
        validateSuccess(){
            let msg = ''
            if(this.$refs.uploader.files.length == 0){
                msg = "Seleccione un ARCHIVO"
            } else if(this.channel.label == 'CALL' && this.list.value == undefined){
                msg = "Seleccione una LISTA"
            } else if(this.channel.label == 'CALL' && this.carrier.value == undefined){
                msg = "Seleccione un PROVEEDOR"
            } else if(this.channel.value == undefined){
                msg = "Seleccione un CANAL"
            // }else if(this.iterations < 0 || this.iterations > 10){
            //     msg = "Corrija el campo de iteraciones"
            // } else if(this.seconds < 60 || this.seconds > 10000){
            //     msg = "Corrija el campo de horas"
            } else if(!this.dbName){
                msg = "Problemas internos. Intente más tarde."
            }else{
                return {status: true}
            }

            return {status: false, msg: msg}
        },
        upload() {
            this.isReport = false
            this.loading = true
            
            this.report.msg = 'NA'
            this.report.time = 'NA'
            this.report.clients = 'NA'
            this.report.products = 'NA'
            this.report.duplicates = 'NA'
            this.report.out = 'NA'
            this.report.process = 'NA'
            this.report.show = false

            let res = this.validateSuccess()

            if (res.status) {
                let file = this.$refs.uploader.files[0]
                let data = new FormData()

                data.append("file", file)
                data.set("iterations", this.iterations)
                data.set("seconds", this.seconds)
                data.set("list_id", this.list.value == undefined ? 0 : this.list.value)
                data.set("carrier_id", this.carrier.value == undefined ? 0 : this.carrier.value)
                data.set("entity_prefix", this.dbName)
                data.set("channel_id", this.channel.value)
                data.set("matched_columns", JSON.stringify({
                    code : this.dataColumn.code.field,
                    name : this.dataColumn.name.field,
                    product : this.dataColumn.product.field,
                    amount : this.dataColumn.amount.field,
                    currency : this.dataColumn.currency.field,
                    date : this.dataColumn.date.field,
                    phone : this.dataColumn.phone.field
                }))

                this.axios.post(`${API_URL}/carga`, data, {
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
                        "Content-Type": "multipart/form-data"
                    }
                })
                .then(res => {
                    if (res.data.status) {
                        this.isError = false
                        this.iterations = ""
                        this.seconds = ""
                        this.carrier = ""
                        this.list = ""
                        this.channel = ""
                        this.$refs.uploader.reset()
                        this.chargeLoadedClass = "positive"
                        this.$q.notify({
                            position: 'top',
                            color: 'positive',
                            message: 'Se creó la lista!',
                            timeout: 2000,
                        })
                        this.allowMatch = false
                    } else {
                        this.chargeLoadedClass = "negative"
                        this.$q.notify({
                            position: 'top',
                            color: 'negative',
                            message: 'Error! Verifique los datos',
                            timeout: 2500,
                            actions: [{ icon: 'close', color: 'white' }]
                        })
                    }
                    this.report.time = res.data.time != undefined ? res.data.time : 'NA'
                    this.report.clients = res.data.count_clients != undefined ? res.data.count_clients : 'NA'
                    this.report.products = res.data.count_products != undefined ? res.data.count_products : 'NA'
                    this.report.duplicates = res.data.count_duplicates != undefined ? res.data.count_duplicates : 'NA'
                    this.report.out = res.data.count_out != undefined ? res.data.count_out : 'NA'
                    this.report.msg = res.data.msg != undefined ? res.data.msg : 'NA'
                    this.report.process = res.data.process != undefined ? res.data.process : 'NA'
                    this.report.show = true
                    this.isReport = true
                })
                .then(() => {
                    this.loading = false
                    this.isReport = true
                }).catch(()=>{
                    this.loading = false
                    this.isReport = true
                })
            } else {
                this.loading = false
                this.$q.notify({
                    position: 'top',
                    color: 'warning',
                    message: res.msg != undefined ? res.msg : 'Complete los campos',
                    timeout: 2500,
                    actions: [{ icon: 'close', color: 'white' }]
                })
            }
        },
        onFileSelected(){
            this.allowMatch = true
            this.btnMatchLoad = true
            let file = this.$refs.uploader.files[0]
            let reader = new FileReader()
            reader.onload = () => {
                let workbook = XLSX.read(reader.result, {type:"buffer"})
                let sheet = workbook.Sheets[workbook.SheetNames[0]]
                let rows = XLSX.utils.sheet_to_json(sheet, {header:1})
                if(rows.length){
                    this.excelColumns = rows[0]
                    this.dialogStatus = true
                }
                this.btnMatchLoad = false
            }
            reader.readAsArrayBuffer(file)
        },
        clickData(key){
            if(!this.dataColumn[key].field){
                if(!this.dataColumn.prevSelected){
                    this.dataColumn[key].class = this.dataColumn[key].clickClass
                    this.dataColumn.prevSelected = key
                }else if(this.dataColumn.prevSelected == key && !this.dataColumn[key].field){
                    this.dataColumn.prevSelected = ''
                    this.dataColumn[key].class = 'grey'
                }
            }
        },
        tryMatch(field){
            if(this.dataColumn.prevSelected){
                this.dataColumn[this.dataColumn.prevSelected].field = field
                this.$set(this.dataColMatch, field, this.dataColumn[this.dataColumn.prevSelected].class)
                this.dataColumn.prevSelected = ''
            }
        },
        resetMatcher(){
            this.dataColumn = {
                code: {
                    field: '',
                    class: 'grey',
                    clickClass: 'blue-grey-10'
                },
                name: {
                    field: '',
                    class: 'grey',
                    clickClass: 'red'
                },
                product: {
                    field: '',
                    class: 'grey',
                    clickClass: 'orange-9'
                },
                amount: {
                    field: '',
                    class: 'grey',
                    clickClass: 'brown-8'
                },
                currency: {
                    field: '',
                    class: 'grey',
                    clickClass: 'blue-8'
                },
                date: {
                    field: '',
                    class: 'grey',
                    clickClass: 'green-8'
                },
                phone: {
                    field: '',
                    class: 'grey',
                    clickClass: 'secondary'
                },
                prevSelected: ''
            }
            this.dataColMatch = {}
        }
    }
}