import Vue from 'vue'
import App from './App.vue'
import './quasar'
import router from './router'

import VueAxios from 'vue-axios'
import axios from 'axios'

Vue.use(VueAxios, axios)

export const bus = new Vue()

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
  router
}).$mount('#app')
