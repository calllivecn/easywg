import Vue from 'vue'
import Router from 'vue-router'
import showtime from '@/components/showtime'
import auth from '@/components/auth'
import login from '@/components/login'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: "/login",
      name: "login",
      component: login
    },
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
