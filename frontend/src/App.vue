<template>
    <div id="app" class="show">
      <p>{{prompt}}</p>
      <router-view></router-view>
    </div>
</template>

<script>

export default {
    name: 'App',
    data(){
      return {
        prompt: "",
      }
    },
    created: function(){
      var vm = this
      this.axios.get("/accounts/logined/")
      .then(function(res){
          if(res.data.code == 0){
            vm.$router.push({name: "home"})
            console.log("路由跳转： name->home")
          }else{
            vm.$router.push({path: "/login"})
            console.log("路由跳转： /login")
          }
      }, function(){
          vm.prompt = "服务器出错！"
      })
    },
}
</script>

<style>
#app {
  /*
  color: #2c3e50;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  position: relative;
  */
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  text-align: center;

  padding: 2px;
  margin: auto;
  position: absolute;
  top: 0px;
  left: 0px;
  right: 0px;

  width: 95%;
}
input{  
    background:none;  
    outline:none;  
    border:none;
}
select{  
    background:none;  
    outline:none;  
    border:none;
}
textarea{  
    background:none;  
    outline:none;  
    border:none;
}
button {
  margin: 0;
  padding: 0;
  border: transparent;  /* 自定义边框 */
  outline: none;    /* 消除默认点击蓝色边框效果 */
  background-color: transparent;
}
.show_bak {
  border-style: solid;
  border-width: 1px;
  border-color: black;
}
</style>