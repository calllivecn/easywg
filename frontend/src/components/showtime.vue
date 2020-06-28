<template>
  <div class="show">
    <h1 >{{ msg }}</h1>
    <h2>Essential Links</h2>
  </div>
</template>

<script>
export default {
  name: 'showtime',
  data () {
    return {
      msg: 'Welcome to Your Vue.js App'
    }
  },
  mounted: function(){
    console.log("hello mounted done.")
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only
<style scoped> -->