<template>
    <div id="center" class="show">

        <div id="leftmenu" class="show" v-if="superuser">
            <label v-on:click="myinterfaces"><u>My WireGuard</u></label>
            <br>
            <label v-on:click="serverwg"><u>Server WireGuard</u></label>
        </div>

        <div id="context" class="show something">

            <server-list-delete v-if="WG == 'S_LIST'" v-on:server-list="serverwg" v-on:server-add="serveradd" v-on:server-change="serverchange"></server-list-delete>
            <server-change-add v-if="WG == 'S_CHANGE'" v-on:server-list="serverwg" v-bind:ifaceinfo="ifaceinfo"></server-change-add>
            

            <table v-if="WG == 'C_LIST'">
                <tr><th>接口名</th><th>启用的网络</th><th>描述</th><th>conf配置</th></tr>

                <tr v-for="iface in data" v-bind:key="iface.iface">
                    <td>{{ iface.name }}</td>
                    <td>Allowed-ips: {{ iface.allowedips }}</td>
                    <td>{{ iface.comment }}</td>
                    <td v-on:click="conf(iface.name)">下载配置</td>
                </tr>
            </table>

        </div>

    </div>
</template>


<script>
import server_change_add from '@/components/server-change-add'
import server_list_delete from '@/components/server-list-delete'

export default {
    name: "center",
    data: function(){
        return {
            superuser: null,
            data: '',
            WG: 'C_LIST',
        }
    },
    components:{
        "server-change-add": server_change_add,
        "server-list-delete": server_list_delete,
    },
    mounted: function(){
        var vm = this
        this.superuser = sessionStorage.superuser
        this.axios.get("/myinterfaces/")
        .then(function(res){
            if(res.data.code == 0){
                vm.data = res.data.data
            }else{
                console.log("Error:", res.data.msg)
            }
        })
    },
    methods:{
        myinterfaces: function(){
            this.WG = "C_LIST"
        },
        serverwg: function(){
            this.WG = "S_LIST"
        },
        serveradd: function(){
            this.WG = 'S_CHANGE'
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