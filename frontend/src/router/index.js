import Vue from 'vue'
import Router from 'vue-router'

import home from '@/components/home'
import login from '@/components/login'

Vue.use(Router)

export default new Router({
    //mode: "history",
    routes: [
        {
            path: "/",
            redirect: "/login"
        },
        {
            path: '/easywg',
            name: 'home',
            component: home
        },
        {
            path: "/login",
            name: "login",
            component: login
        },
    ]
})
