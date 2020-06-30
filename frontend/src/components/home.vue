<template>
  <div id="home" class="show">
    <div id="header" class="show">
      <vheader></vheader>
    </div>

    <center></center>

    <div id="bottom" class="show">
      <auth></auth>
    </div>
  </div>
</template>

<script>
import vheader from "@/components/vheader"
import center from '@/components/center'
import auth from '@/components/auth'

export default {
  name: 'home',
  components: {
    vheader,
    center,
    auth,
  }
}
</script>

<style>
#header {
  position: relative;
  top: 1px;
  height: 4em;
  width: 100%;
}

#bottom {
  position: relative;
  top: 1px;
  width: 100%;
}

</style>
