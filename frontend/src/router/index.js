import Vue from 'vue'
import Router from 'vue-router'
import showtime from '@/components/showtime'
import auth from '@/components/auth'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'showtime',
      component: showtime
    },
    {
      path: "/auth",
      name: "auth",
      component: auth
    }
  ]
})
