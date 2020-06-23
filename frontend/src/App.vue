<template>
  <div id="app" class="show">
    <div id="header" class="show">
      <vheader></vheader>
    </div>

    <div id="center" class="show">
      <leftmenu class="show"></leftmenu>
      <!-- <router-view id="context" class="show"></router-view> -->
      <div id="print" class="show">
        <showtime></showtime>
      </div>
    </div>

    <div id="bottom" class="show">
      <router-link to="login">登录</router-link>
      <router-view></router-view>
      <auth></auth>
    </div>
  </div>
</template>

<script>
import vheader from "@/components/vheader"
import leftmenu from "@/components/leftmenu"
import showtime from '@/components/showtime'
import auth from '@/components/auth'

export default {
  name: 'App',
  components: {
    vheader,
    leftmenu,
    showtime,
    auth,
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

#header {
  position: relative;
  top: 1px;
  height: 4em;
  width: 100%;
}

#center {
  position: relative;
  width: 100%;
  display: flex;
}

#print {
  display: inline;
  width: 100%;
}

#bottom {
  position: relative;
  top: 1px;
  width: 100%;
}

.show {
  border-style: solid;
  border-width: 1px;
  border-color: black;
}
</style>
