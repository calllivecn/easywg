<template>
    <div id="userinfo" class="show">
        <div id="username">
            <span v-if="this.username">用户：{{ username }}</span>
        </div>
        <div id="logout">
            <button v-if="this.username" v-on:click="logout">点击退出</button>
            <button v-else v-on:click="login">点击登录</button>
            <span> | </span>
            <button v-on:click="chpassword">修改密码</button>
        </div>
    </div>
</template>


<script>
    export default {
        name: "v-header",
        data: function () {
            return {
                username: ""
            }
        },
        created: function () {
        },
        mounted: function () {
            this.username = sessionStorage.username
        },
        methods: {
            login: function () {
                this.$router.push({ name: "login" })
            },
            logout: function () {
                var vm = this
                this.axios.get("/accounts/logout/")
                    .then(function (res) {
                        if(res.data.code == 0){
                            console.log("退出")
                            sessionStorage.clear()
                            vm.$router.push({ name: "login" })
                        }
                    },function(){
                        console.log("退出失败, 服务端出错！")
                    })

            },
            chpassword: function(){
                this.$router.push({name: "chpassword"})
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