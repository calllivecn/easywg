<template>
    <div id="leftmenu">
        <label v-on:click="serverwg"><u>Server WireGuard</u></label>
        <br>
        <label v-on:click="myinterfaces"><u>My WireGuard</u></label>
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
        serverwg:function(){
            this.router.push({paht: "/serverwg"})
        },
        myinterfaces:function(){
            this.router.push({path: "/myinterfaces"})
        },
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