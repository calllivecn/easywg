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
    name: "bar",
    data: function(){
        return {
            usertype: "游客",
            username: "无名"
        }
    },
    methods:{
        logout: function(){
            this.axios.get("/logout")
            .then(function(){
                console.log("退出")
                this.router.push({path: "/"})
            })
            .catch(function(){
                console.log("退出失败")
                this.router.push({path: "/"})
            })
        }
    }

}
</script>


<style>
#userinfo {
    position: absolute;
    right: 1%;

    border-style: solid;
    border-width: 1px;
    border-color: black;
}
</style>