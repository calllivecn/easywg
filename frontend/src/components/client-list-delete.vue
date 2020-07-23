<template>
    <div>
        <header>Peer 信息</header>
        <p>{{ prompt }}</p>
        <button v-on:click="add">添加</button>
        <div v-for="data in datas" v-bind:key="data.serverwg">
            <p>
            <div style="text-align: center;">
                <label>Server: {{ data.serverwg }} </label>
                <label>address: {{ data.address }}</label>
                <label>IP: {{ data.ip }}</label>
                <label>publickey: {{ data.publickey }}</label>
            </div>
            </p>
            <table style="margin: auto">
                <tr>
                    <th>接口名</th>
                    <th>IP</th>
                    <th>publickey</th>
                    <th>Allowed-ips</th>
                    <th>描述</th>
                    <th>删除 peer</th>
                    <th>conf配置</th>
                </tr>

                <tr v-for="iface in data.ifaces" v-bind:key="iface.iface">
                    <td>{{ iface.iface }}</td>
                    <td>{{ iface.ip }}</td>
                    <td>{{ iface.publickey }}</td>
                    <td>{{ iface.allowedips }}</td>
                    <td>{{ iface.comment }}</td>
                    <td>
                        <span v-on:click="remove(data.id, iface.id)">删除</span>
                        <!--
                        <span> - </span>
                        <span v-on:click="change(data.id, iface)">修改</span>
                        -->
                    </td>
                    <td>
                        <a v-bind:href="'/client/conf/?iface=' + iface.iface + '&format=conf'" target="_blank">下载配置</a>
                        <span> | </span>
                        <span v-on:click="qrcode(iface.iface)">二维码配置</span>
                        <span> | </span>
                        <a v-bind:href="'/client/conf/?iface=' + iface.iface + '&format=shell'">shell配置</a>
                    </td>
                </tr>
            </table>
        </div>
        <popwin  v-show="show" v-model:title="title">
            <div v-html="text"></div>
        </popwin>
    </div>
</template>

<script>
import eventbus from '../js/eventbus.js'
import popwin from '@/components/popwin'
export default {
    name: "client-list-delete",
    data: function(){
        return {
            prompt: null,
            datas: [],

            show: false,
            title: "弹窗title",
            text: '<img></img>'
        }
    },
    components:{
        popwin,
    },
    created: function(){
        var vm = this
        eventbus.$on("popwin", function(yesno){
            vm.show = yesno
        })
    },
    mounted: function(){
        var vm = this
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
            eventbus.etype('client-add')
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
        qrcode: function(iface){
            var vm = this
            console.log("popwin")
            // 拿 qrcode
            this.axios.get("/client/conf/", {params: {
                "iface": iface,
                "format": "qrcode"
              }})
            .then(function(res){
                vm.text = '<img src="data:image/png;base64,' + res.data + '"></img>'
                vm.show = true
            },function(res){
                vm.prompt = res.data.msg
            })
        }
    }
}
</script>

<style>
    a {
        text-decoration: none;
        color: black;
    }
</style>
