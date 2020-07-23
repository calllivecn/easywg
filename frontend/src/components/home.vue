<template>
  <div id="home" class="show">
    <div id="header" class="show">
      <vheader></vheader>
    </div>

    <center></center>

  </div>
</template>

<script>
import vheader from "@/components/vheader"
import center from '@/components/center'

export default {
  name: 'home',
  components: {
    vheader,
    center,
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
