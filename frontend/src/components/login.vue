<template>
    <div id="login" class="show">
        <p>{{ prompt }}</p>
        <span>用户名：</span><input v-model="username" placeholder="请输入用户名">
        <br>
        <span>密码：</span><input v-model="password" type="password" placeholder="请输入密码">
        <br>
        <button v-on:click="login">登录</button>
    </div>
</template>

<script>
export default {
    name: "login",
    data: function(){
        return {
            username: "",
            password: "",
            prompt: "",
        }
    },
    created: function(){
        var vm = this
        this.axios.get("/accounts/logined/")
            .then(function (res) {
                if(res.data.code == 0) {

                    sessionStorage.username = res.data.username
                    sessionStorage.superuser = res.data.superuser
                    sessionStorage.logined = '1'

                    vm.$router.push({ name: "home" })
                    console.log("路由跳转： name->home")
                }
            })
    },
    methods:{
        login: function(){
            var vm = this
            this.axios.post("/accounts/login/", {
                "un": this.username,
                "pw": this.password
            })
            .then(
                function(res){
                    if(res.data.code == 0){
                        sessionStorage.username = vm.username
                        sessionStorage.superuser = res.data.superuser
                        sessionStorage.logined = '1'
                        vm.$router.push({name: "home"})
                        console.log(vm.username)
                    }else {
                        vm.prompt = "用户名或密码错误！"
                    }
                },
                function(res){
                    console.log("请求出错")
                    vm.prompt = "请求出错！"
                }
            )
        }
    }
}
</script>

<style>
input{  
    background:none;  
    outline:none;  
    border:none;
}
#login {
    position: relative;
    top: 4rem;
}
button {
  margin: 0;
  padding: 0;
  border: transparent;  /* 自定义边框 */
  outline: none;    /* 消除默认点击蓝色边框效果 */
  background-color: transparent;
}
</style>