<template>
    <div>
        <header>Peer 信息</header>
        <p>{{ prompt }}</p>
        <button v-on:click="add">添加</button>
        <div v-for="data in datas" v-bind:key="data.serverwg">

            <div style="text-align: left;">
                <label>Server: {{ data.serverwg }} </label>
                <label>ip: {{ data.net }}</label>
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

                <tr v-for="iface in data.ifaces" v-bind:key="data.ifaces.iface">
                    <td>{{ iface.name }}</td>
                    <td>{{ iface.ip }}</td>
                    <td>{{ iface.allowedips }}</td>
                    <td>{{ iface.comment }}</td>
                    <td v-on:click="conf(iface.name)">下载配置</td>
                    <td><span v-on:change="change">修改</span><span> - </span><span v-on:remove="remove">删除</span></td>
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

        eventbus.$on("client-change-data", function(iface){
            for(let i in vm.datas){
                if(vm.datas[i].id == iface.id){
                    vm.data.splice(i, 1, iface)
                    return
                }
            }
            vm.data.push(iface)
            vm.data.sort(function(a, b){return a.id - b.id})
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
        remove: function(){
            
        },
        change: function(){

        },
        conf: function(){
            var vm = this
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