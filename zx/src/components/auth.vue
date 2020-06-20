<template>
    <div>
        <h1 v-text="title">Authenticate</h1>
        <label id="showget">
            {{ dataget }}
        </label>
        <br/>
        <button v-on:click="get">从后台全数据</button>
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
        methods: {
            get: function(){
                this.axios.defaults.baseURL = "http://127.0.0.1:8880/"

                this.axios.get("/auth")
                .then(
                    function(res){
                        console.log("res:", res)
                        this.dataget = res
                    },
                    function(res){
                        console.log("this: ", this)
                        console.log("error")
                    })
            }
        },
    }

</script>
