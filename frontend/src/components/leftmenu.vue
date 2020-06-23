<template>
    <div id="leftmenu">
        <nobr v-on:click="serverwg"><u>Server WireGuard</u></nobr>
        <nobr v-on:click="myinterfaces"><u>My WireGuard</u></nobr>
    </div>
</template>


<script>
export default {
    name: "leftmenu",
    data: function(){
        return {

        }
    },
    methods:{
        myinterfaces:function(){
            this.router.push({path: "/myinterfaces"})
        },
        serverwg:function(){
            this.router.push({paht: "/serverwg"})
        }
    }

}
</script>


<style>
#leftmenu {
    display: inline;
    text-align: left;
    text-decoration: underline;
    /*
    width: 1rem;
    position: relative;
    left: 1pm;
    */
}
</style>