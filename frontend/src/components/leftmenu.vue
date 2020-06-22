<template>
    <div id="leftmenu">
        <label v-on:click="myinterfaces">My WireGuard</label>
        <label v-on:click="serverwg">Server WireGuard</label>
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


