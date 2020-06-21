<template>
  <div id="app">
    <div id="header">
      <v-header></v-header>
    </div>

    <div id="router-view">
      <router-view/>
    </div>

    <div id=auth>
      <auth></auth>
    </div>
  </div>
</template>

<script>
import bar from "@/components/bar"
import HelloWorld from '@/components/HelloWorld'
import auth from '@/components/auth'

export default {
  name: 'App',
  components: {
    "v-header": bar,
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
  margin-top: 60px;
}
#header {
    width: 100%;
    height: 10%;

    position: sticky;
    top: 0%;

    border-style: solid;
    border-width: 1px;
    border-color: black;
}
</style>
