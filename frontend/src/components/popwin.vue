<template>
    <div class="show popwin" v-show="show">
        <header>{{ title }}</header>
        <div v-html="text"></div>
        <div>
            <slot></slot>
        </div>
        <button @click="ok">关闭</button>
    </div>
</template>
<script>
import eventbus from '../js/eventbus.js'
export default {
    props: ['show', 'title', 'text'],
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
    text-align: center;
    position: fixed;
    z-index: 1;
    top: 50%;
    left: 50%;
    transform: translate(-50%,-50%);
}
</style>