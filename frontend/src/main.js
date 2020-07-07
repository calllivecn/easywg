// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

// myfunction
import funcs from './js/funcs.js'

// 第一种方式
//import axios from 'axios'
//import VueAxios from 'vue-axios'
//Vue.use(VueAxios, axios)

import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


Vue.prototype.axios = axios 
Vue.prototype.funcs = funcs

Vue.config.productionTip = false

/* eslint-disable no-new */
var vue = new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App></App>'
})
