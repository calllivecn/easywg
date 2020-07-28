<template>
    <div id="center" class="show">

        <div id="leftmenu" class="show" >
            <button v-if="superuser" v-on:click="currentComponent = 'server-list-delete'"><h3><u>Server WireGuard</u></h3></button>
            <br>
            <button v-on:click="currentComponent = 'client-list-delete'"><h3><u>My Peer WireGuard</u></h3></button>
        </div>

        <div id="context" class="show something">

            <component v-bind:is="currentComponent"></component>
            <!--
            <keep-alive>
            </keep-alive>
            -->
        </div>

    </div>
</template>


<script>
import eventbus from '../js/eventbus.js'
import server_list_delete from '@/components/server-list-delete'
import server_change_add from '@/components/server-change-add'
import client_list_delete from '@/components/client-list-delete'
import client_change_add from '@/components/client-change-add'

export default {
    name: "center",
    data: function(){
        return {
            superuser: null,
            currentComponent: "client-list-delete",
        }
    },
    components:{
        "server-list-delete": server_list_delete,
        "server-change-add": server_change_add,
        "client-list-delete": client_list_delete,
        "client-change-add": client_change_add,
    },
    created: function(){
        // 根据事件动态渲染
        var vm = this
        eventbus.$on('event-change', function(event){
            console.log("center.vue 接收事件：", event)
            vm.currentComponent = event
        })
    },
    mounted: function(){
        this.superuser = sessionStorage.superuser
    },
    methods:{
    },
}
</script>

<style>

#center {
  position: relative;
  width: 100%;
  display: flex;
}

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

#context {
  display: inline;
  width: 80%;
}

.something {
  text-align: center;
}

</style>