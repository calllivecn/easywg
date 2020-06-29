<template>
    <div id="auth">
        <p v-text="title">Authenticate</p>
        <p id="showget">{{ dataget }}</p>
        <button v-on:click="get">验证当前用户</button>
    </div>
</template>

<script>
    export default {
        name: "auth",
        data: function(){
            return {
                title: "这是 data() 渲染的",
                dataget: "没执行前的数据值",
            }
        },
        mounted: function(){
            console.log("Auth 组件 mounted完成")
        },
        methods: {
            get: function(){
                var vm = this
                this.axios.post("/accounts/auth/")
                .then(
                    function(res){
                        console.log("this:", vm)
                        vm.dataget = res.data
                    },
                    function(res){
                        console.log("error")
                        vm.dataget = res
                    })
            }
        },
    }

</script>
