<template>
    <div id="userinfo" class="show">
            <div id="username">
                <label>用户： {{ username }}</label>
            </div>
            <div id="logout">
                <!-- <label v-on:click="logout">点击退出</label> -->
                <button v-on:click="logout">点击退出</button>
            </div>
    </div>
</template>


<script>
export default {
    name: "v-header",
    data: function(){
        return {
            username: "游客"
        }
    },
    methods:{
        logout: function(){
            var vm = this
            this.axios.get("/logout")
            .then(function(){
                console.log("退出")
                vm.$router.push({path: "/"})
            })
            .catch(function(){
                console.log("退出失败")
                vm.$router.push({path: "/"})
            })
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