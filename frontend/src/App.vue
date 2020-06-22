<template>
  <div id="app" class="show">
    <div id="header" class="show">
      <vheader></vheader>
    </div>

    <leftmenu class="show"></leftmenu>

    <!-- <router-view id="context" class="show"></router-view> -->
    <HelloWorld id="context" class="show"></HelloWorld>

    <div id=auth class="show">
      <auth></auth>
    </div>
  </div>
</template>

<script>
import vheader from "@/components/vheader"
import leftmenu from "@/components/leftmenu"
import HelloWorld from '@/components/HelloWorld'
import auth from '@/components/auth'

export default {
  name: 'App',
  components: {
    vheader,
    leftmenu,
    HelloWorld,
    auth,
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0px;

  width: 100%;

  position: relative;
  top: 0%;
}
#header {
  height: 4vw;
  width: 100%;

  position: relative;
  top: 0%;

}
#leftmenu {
  position: relative;
  top:0%;
  left: 0px;
  width: 200px;
}
#context {
  position: relative;
  left: 200px;
  right: 0px;

}
#router-view {
  position: relative;
  right: 0px;
}
.show{
  border-style: solid;
  border-width: 1px;
  border-color: black;
}
</style>
