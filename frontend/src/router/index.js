import Vue from 'vue'
import Router from 'vue-router'

import home from '@/components/home'
import login from '@/components/login'
import chpassword from '@/components/chpassword'
import notfound from '@/components/notfound'

Vue.use(Router)

export default new Router({
    mode: "history",
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
        {
            path: "/chpassword",
            name: "chpassword",
            component: chpassword
        },
        {
            path: '*',
            component: notfound
        }
    ]
})
