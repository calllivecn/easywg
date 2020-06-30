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
.show {
  border-style: solid;
  border-width: 1px;
  border-color: black;
}
</style>