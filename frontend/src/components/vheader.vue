<template> 
    <div id="userinfo" class="show">
        <div id="username">
            <span v-if="this.username != null">用户：{{ username }}</span>
        </div>
        <div id="logout">
            <button v-if="this.username == null" v-on:click="login">点击登录</button>
            <button v-else v-on:click="logout">点击退出</button>
        </div>
    </div>
</template>


<script>
export default {
    name: "v-header",
    data: function(){
        return {
            username: null
        }
    },
    created: function(){
        if(sessionStorage.logined != '1'){
            this.$router.push({path: "/login"})
        }
    },
    mounted: function(){
        this.username = sessionStorage.username
    },
    methods:{
        login: function(){
            this.$router.push({path: "/login"})
        },

        logout: function(){
            var vm = this
            this.axios.get("/accounts/logout")
            .then(function(){
                console.log("退出")
                localStorage.clear()
                vm.$router.push({name: "login"})
            })
            .catch(function(){
                console.log("退出失败")
                vm.$router.push({name: "login"})
            })
        }
    }
}
</script>


<style>
#userinfo {
    position: absolute;
    right: 1px;
    height: 4rem;
}

#username {
    position: relative;
    top: 1px;
}

#logout {
    position: relative;
    bottom: 1px;
}
</style>