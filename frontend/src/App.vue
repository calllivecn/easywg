<template>
  <div id="app">
    <auth></auth>
    <router-view/>
  </div>
</template>

<script>
import auth from '@/components/auth'

export default {
  name: 'App',
  components: {
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
</style>
