<template>
    <div id="userinfo" class="show">
            <div id="username">
                <span>用户： {{ username }}</span>
            </div>
            <div id="logout">
                <!-- <login v-if="this.username == '游客'" v-on:click="login">点击登录</login> -->
                <span v-if="this.username == '游客'" v-on:click="login">点击登录</span>
                <span v-else v-on:click="logout">点击退出</span>
            </div>
    </div>
</template>


<script>
export default {
    name: "v-header",
    data: function(){
        return {
            username: "游客"
        }
    },
    methods:{
        login: function(){
            console.log("this.$router:", this.$router)
            this.$router.push({path: "/login"})
        },
        logout: function(){
            var vm = this
            this.axios.get("/logout")
            .then(function(){
                console.log("退出")
                vm.$router.push({path: "/logout"})
            })
            .catch(function(){
                console.log("退出失败")
                vm.$router.push({path: "/"})
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