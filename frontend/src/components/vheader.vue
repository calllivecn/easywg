<template>
    <div id="userinfo">
            <label id="usertype">{{ usertype }}</label>
            <br>
            <label id="username">用户： {{ username }}</label>
            <br>
            <label id="logout" v-on:click="logout">退出</label>
    </div>
</template>


<script>
export default {
    name: "v-header",
    data: function(){
        return {
            usertype: "游客",
            username: "无名"
        }
    },
    methods:{
        logout: function(){
            var vm = this
            this.axios.get("/logout")
            .then(function(){
                console.log("退出")
                vm.router.push({path: "/"})
            })
            .catch(function(){
                console.log("退出失败")
                vm.router.push({path: "/"})
            })
        }
    }

}
</script>


<style>
#userinfo {
    position: absolute;
    right: 0%;

    height: 4vw;
    width: 4vw;

    border-style: solid;
    border-width: 1px;
    border-color: black;
}
</style>