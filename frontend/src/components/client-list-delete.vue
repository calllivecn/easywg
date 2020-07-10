<template>
    <div>
        <header>Peer 信息</header>
        <p>{{ prompt }}</p>
        <button v-on:click="add">添加</button>
        <div v-for="data in datas" v-bind:key="data.serverwg">

            <div style="text-align: left;">
                <label>Server: {{ data.serverwg }} </label>
                <label>address: {{ data.address }}</label>
                <label>network: {{ data.network }}</label>
                <label>publickey: {{ data.publickey }}</label>
            </div>
            <table>
                <tr>
                    <th>接口名</th>
                    <th>IP</th>
                    <th>Allowed-ips</th>
                    <th>描述</th>
                    <th>conf配置</th>
                    <th>CURD没有CR</th>
                </tr>

                <tr v-for="iface in data.ifaces" v-bind:key="iface.iface">
                    <td>{{ iface.name }}</td>
                    <td>{{ iface.ip }}</td>
                    <td>{{ iface.allowedips }}</td>
                    <td>{{ iface.comment }}</td>
                    <td v-on:click="conf(iface.name)">下载配置</td>
                    <td>
                        <span v-on:click="change(data.id, iface)">修改</span>
                        <span> - </span>
                        <span v-on:click="remove(data.id, iface.id)">删除</span>
                    </td>
                </tr>
            </table>
        </div>
    </div>
</template>

<script>
import eventbus from '../js/eventbus.js'
export default {
    name: "client-list-delete",
    data: function(){
        return {
            prompt: null,
            datas: [],
        }
    },
    created: function(){
        var vm = this

        eventbus.$on('event-change', function(e){
            vm.prompt = ""
        })

        eventbus.$on("client-change-data", function(arg){
            console.log("arg:", arg)

            serverid = arg.serverid
            iface = arg.iface

            // add
            for(let i in this.datas){
                if(serverid == this.datas[i].id){
                    server.push(iface)
                    server.sort(function(a, b){return a.id - b.id})
                }
            }
        })

        //初始化 数据
        this.axios.get("/clientwg/")
        .then(function(res){
            if(res.data.code == 0){
                vm.datas = res.data.data
            }else{
                vm.prompt = res.data.msg
            }
        },function(res){
            vm.prompt = "服务器出错！"
        })
    },
    methods: {
        add: function(){
            var vm = this 
            eventbus.$emit("event-change", "client-change-add")
        },
        remove: function(serverid, ifaceid){
            console.log("删除ifaceid：",ifaceid)
            var vm = this

            this.axios.delete("/clientwg/", {data:{"ifaceid": ifaceid}})
            .then(function(res){
                if(res.data.code == 0){

                    for(let i in vm.datas){

                        if(serverid == vm.datas[i].id){

                            for(let j in vm.datas[i].ifaces){
                                if(ifaceid == vm.datas[i].ifaces[j].id){
                                    vm.datas[i].ifaces.splice(j, 1)
                                    return
                                }
                            }
                        }
                    }

                }else{
                    vm.prompt = res.data.msg
                }

            }, function(){
                vm.prompt = "服务器出错！"
            })

            
        },
        change: function(){

        },
        conf: function(ifacename){
            var vm = this
            console.log("conf: ", ifacename)
            return 
            this.axios.get("/client/conf/",{
                params:{
                    "os": "",
                    "format": "",
                }
            })
        },
    }
}
</script>