<template>
  <div id="home" class="show">
    <div id="header" class="show">
      <vheader></vheader>
    </div>

    <div id="center" class="show">
      <leftmenu class="show"></leftmenu>
      <div id="print" class="show">
        <showtime></showtime>
      </div>
    </div>

    <div id="bottom" class="show">
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
  name: 'home',
  components: {
    vheader,
    leftmenu,
    showtime,
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

#center {
  position: relative;
  width: 100%;
  display: flex;
}

#print {
  display: inline;
  /* width: 100%; */
}

#bottom {
  position: relative;
  top: 1px;
  width: 100%;
}

</style>
