<template>
    <div id="auth">
        <p v-text="title"></p>
        <p id="showget">{{ dataget }}</p>
        <button v-on:click="get">验证当前用户</button>
    </div>
</template>

<script>
    export default {
        name: "auth",
        data: function(){
            return {
                title: "Authenticate",
                dataget: "没执行前的数据值",
            }
        },
        mounted: function(){
        },
        methods: {
            get: function(){
                var vm = this
                this.axios.post("/accounts/auth/")
                .then(
                    function(res){
                        vm.dataget = res.data
                        console.log(res.data)
                    },
                    function(res){
                        vm.dataget = res.data.msg
                    })
            }
        },
    }

</script>
