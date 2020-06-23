<template>
    <div id="login">
        <p v-if="prompt">用户名或密码错误！</p>
        <span><input v-model="username" placeholder="请输入用户名"></span>
        <span><input v-model="password" type="password" placeholder="请输入用户名"></span>
        <span><input type="submit" @click="login" placeholder="请输入用户名"></span>
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
            this.axios.post("/login", {
                "username": this.username,
                "password": this.password
            })
            .then(
                function(data){
                    if(data.code == 0){
                        vm.$router.push({path: "/"})
                    }else {
                        vm.prompt = true
                    }
                },
                function(data){
                    console.log("请求错误")
                    vm.$router.push({path: "/"})
                }
            )
        }
    }
}
</script>