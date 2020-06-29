<template>
    <div id="userinfo" class="show">
            <div id="username">
                <span v-if="this.username != null">用户：{{ username }}</span>
            </div>
            <div id="logout">
                <span v-if="this.username == null" v-on:click="login">点击登录</span>
                <span v-else v-on:click="logout">点击退出</span>
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
        /*
        console.log("created: 执行了吗？", typeof(this.username))
        if(typeof(this.$route.params.username) == "undefined"){

            this.$router.push({path: "/login"})
        }
        */

        if(!document.cookie.match("session")){
            this.$router.push({path: "/login"})
        }
    },
    mounted: function(){
        console.log("mounted username:", this.$route.params.username)
        this.username = this.$route.params.username
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
                document.cookie = ""
                vm.$router.push({path: "/login"})
            })
            .catch(function(){
                console.log("退出失败")
                vm.$router.push({path: "/login"})
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