<template>
    <div id="login" class="show">
        <p v-if="prompt">用户名或密码错误！</p>
        <span>用户名：</span><input v-model="username" placeholder="请输入用户名">
        <br>
        <span>密码</span><input v-model="password" type="password" placeholder="请输入密码">
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
            prompt: false,
        }
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

                        vm.$router.push({name: "home"})

                        sessionStorage.username = vm.username
                        sessionStorage.superuser = res.data.superuser
                        sessionStorage.logined = '1'

                        console.log(vm.username)
                    }else {
                        //alert("用户名或密码错误")
                        // 这里写一个弹窗 提示用户名或密码错误

                        // 提示密码错误
                        vm.prompt = true
                    }
                },
                function(res){
                    console.log("请求出错")
                }
            )
        }
    }
}
</script>

<style>
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