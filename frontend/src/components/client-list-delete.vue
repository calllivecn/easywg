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
                <tr><th>接口名</th><th>启用的网络</th><th>描述</th><th>conf配置</th><th>CRUD没有CR</th></tr>

                <tr v-for="iface in data.ifaces" v-bind:key="data.ifaces.iface">
                    <td>{{ iface.name }}</td>
                    <td>Allowed-ips: {{ iface.allowedips }}</td>
                    <td>{{ iface.comment }}</td>
                    <td v-on:click="conf(iface.name)">下载配置</td>
                    <td><span v-on:change="change">修改</span><span> - </span><span v-on:remove="remove">删除</span></td>
                </tr>
            </table>
        </div>
    </div>
</template>

<script>
export default {
    name: "client-list-delete",
    data: function(){
        return {
            prompt: null,
            datas: [],
        }
    },
    mounted: function(){
        // this.funcs.myfunc() test ok
        var vm = this
        this.axios.get("/myinterfaces/")
        .then(function(res){
            if(res.data.code == 0){
                vm.datas = res.data.data
            }else{
                vm.prompt = res.data.msg
            }
        },function(res){
            this.prompt = "服务器出错！"
        })
    },
    methods: {
        conf: function(){
            var vm = this
            this.axios.get("/client/conf/",{
                params:{
                    "os": "",
                    "format": "",
                }
            })
        },
        change: function(){

        },
        add: function(){
            
        },
        remove: function(){
            
        },
    }
}
</script>