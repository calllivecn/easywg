<template>
    <div id="chpassword" class="show">
        <p>{{ prompt }}</p>
        <span>当前用户名： {{ username }}</span>
        <br>
        <span>旧密码：</span><input v-model="password1" type="password" placeholder="请输入旧密码">
        <br>
        <span>新密码：</span><input v-model="password2" type="password" placeholder="请输入新密码">
        <br>
        <span>再次输入新密码：</span><input v-model="password3" type="password" placeholder="请再次输入新密码">
        <br>
        <button v-on:click="chpassword">提交</button>
    </div>
</template>

<script>
export default {
    name: "chpassword",
    data: function(){
        return {
            userid: "",
            username: "",
            password1: "",
            password2: "",
            password3: "",
            prompt: "",
        }
    },
    created: function(){
        var vm = this
        if(this.$route.query.initpw){
            this.prompt = "首次登录请修改初始化密码!"
        }
        this.axios.get("/accounts/chpassword/")
            .then(function (res) {
                console.log("res.data: " + res.data.data)
                console.log("userid: ", res.data.data.userid)
                window.resdata = res.data
                if(res.data.code == 0) {
                    vm.userid = res.data.data.userid
                    vm.username = res.data.data.username
                }else{
                    vm.prompt = res.data.msg //"获取用户id失败!"
                }
            }, function(res){
                vm.prompt = "服务器出错！"
            })
            
    },
    methods:{
        chpassword: function(){
            console.log("chpassword() execute~")
            var vm = this

            // check password1 2 3
            if(vm.username == ""){
                vm.prompt = "用户名不能为空！"
                return
            }else if(vm.password1 == ""){
                vm.prompt = "请输入原密码!"
                return
            }else if(vm.password2 != vm.password3){
                vm.prompt = "两次输入密码不一致！请重新输入！"
                return
            }

            this.axios.post("/accounts/chpassword/",{
                "id": vm.userid,
                "un": vm.username,
                "pw1": vm.password1,
                "pw2": vm.password2
            })
            .then(
                function(res){
                    if(res.data.code == 0){
                        sessionStorage.clear()
                        vm.$router.push({ name: "login" })
                        console.log("路由跳转： name->login")
                    }else{
                        vm.prompt = res.data.msg
                    }
                },
                function(res){
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
#chpassword {
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