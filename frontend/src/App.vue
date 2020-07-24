<template>
  <div id="app" class="show">
    <router-view></router-view>
  </div>
</template>

<script>

export default {
  name: 'App',
  mounted: function(){
    //console.log("App.vue 怎么判断用户是否登录??")
  }
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
button {
  margin: 0;
  padding: 0;
  border: transparent;  /* 自定义边框 */
  outline: none;    /* 消除默认点击蓝色边框效果 */
  background-color: transparent;
}
.show {
  border-style: solid;
  border-width: 1px;
  border-color: black;
}
</style>