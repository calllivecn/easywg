<template>
    <div id="center" class="show">

        <div id="leftmenu" class="show" >
            <label v-if="superuser" v-on:click="serverwg"><u>Server WireGuard</u></label>
            <br>
            <label v-on:click="myinterfaces"><u>My Peer WireGuard</u></label>
        </div>

        <div id="context" class="show something">

            <component v-bind:is="currentComponent"></component>

            <server-list-delete v-if="WG == 'S_LIST'" v-on:server-list="serverwg" v-on:server-add="serveradd" v-on:server-change="serverchange"></server-list-delete>
            <server-change-add v-if="WG == 'S_CHANGE'" v-on:server-list="serverwg" v-bind:ifaceinfo="ifaceinfo"></server-change-add>

            <client-list-delete v-if="WG == 'C_LIST'"></client-list-delete>
            <client-change-add v-if="WG == 'C_CHANGE'"></client-change-add>
        </div>

    </div>
</template>


<script>
import {eventbus} from '../js/eventbus.js'
import server_list_delete from '@/components/server-list-delete'
import server_change_add from '@/components/server-change-add'
import client_list_delete from '@/components/client-list-delete'
//import client_change_add from '@/components/client-change-add'

export default {
    name: "center",
    data: function(){
        return {
            superuser: null,
            WG: 'C_LIST',
            currentComponent: "server-list-delete",
        }
    },
    components:{
        "server-list-delete": server_list_delete,
        "server-change-add": server_change_add,
        "client-list-delete": client_list_delete,
        //"client-change-add": client_change_add,
    },
    created: function(){
        console.log("created")
    },
    mounted: function(){
        console.log("mounted")
        this.superuser = sessionStorage.superuser

        eventbus.$on('event-chagne', function(event){
            this.currentComponent = event
        })
    },
    methods:{
        myinterfaces: function(){
            currentComponent = "client-list-delete"
        },
        serverwg: function(){
            this.WG = "S_LIST"
            console.log("server-add")
        },
        serveradd: function(){
            this.WG = 'S_CHANGE'
            this.ifaceinfo = 'S_ADD'
            console.log('父组件 server-add')
        },
        serverchange: function(ifaceinfo){
            this.WG = "S_CHANGE"
            this.ifaceinfo = ifaceinfo
            console.log('父组件 server-change')
        },
    }

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