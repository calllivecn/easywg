<template>
    <!--
    <div class="show popwin" v-on:key.enter="ok" v-on:key.esc="ok" v-on:click="ok">
    -->
    <div class="popwin" v-on:click="ok">
        <slot></slot>
        <span>点击二维码关闭</span>
    </div>
</template>
<script>
import eventbus from '../js/eventbus.js'
export default {
    props: ['title', 'text'],
    data() {
        return {
        }
    },
    methods: {
        ok: function(){
            eventbus.$emit('popwin', false)
        },
    }
}
</script>

<style>
.popwin {
    background-color: aliceblue;
    /* text-align: center; */
    position: fixed;
    z-index: 1;
    top: 30%;
    left: 50%;
    transform: translate(-50%,-50%);
}
</style>