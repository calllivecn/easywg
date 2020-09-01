<template>

    <div>
        <p>{{ prompt }}</p>

        <span>接口名：</span><input v-model="iface.iface" placeholder="留空使用默认接口名">
        <br>

        <span>从属Server:</span>
        <select v-on:change="select($event)">
            <option v-for="wg of wgs" v-bind:value="wg.id" v-text="wg.iface"></option>
        </select>
        <br>

        <span>privatekey: </span>
        <input v-model="iface.privatekey" v-bind:type="showprivatekey" placeholder="私钥(留空为自动生成)">
        <button v-on:click="show('showprivatekey', showprivatekey)">显示私钥</button>
        <br>

        <span>presharedkey: </span><input v-model="iface.presharedkey" v-bind:type="showpresharedkey" placeholder="一般不用输入">
        <button v-on:click="show('showpresharedkey', showpresharedkey)">显示预共享密钥</button>
        <br>

        <!--
        <span>Address</span><input v-model="iface.address" placeholder="Wireguard 使用的ip或域名">
        <br>

        <span>listenport: </span><input v-model="iface.listenport" type="text" placeholder="端口(留空自动生成)">
        <br>

        <span>ip: </span><input v-model="iface.allowedips" type="text" placeholder="ip地址">
        <br>

        <span>client allowed-ips: </span><input v-model="iface.allowedips_c" type="text" placeholder="网络地址">
        <br>

        <span>心跳时间: </span><input v-model="iface.persistentkeepalive" type="text" placeholder="35">
        <br>
        -->

        <span>描述：</span>
        <textarea v-model="iface.comment" placeholder="添加一个简短的描述"></textarea>
        <br>
        <button v-if="op == '添加'" v-on:click="add(iface)">{{ op }}</button>
        <button v-if="op == '修改'" v-on:click="change(iface)">{{ op }}</button>
    </div>
</template>

<script>
import eventbus from '../js/eventbus.js'
export default {
    name: "client-change-add",
    data: function(){
        return {
            prompt: "",
            op: "添加", // or 修改
            wgs: [],
            serverid: null,
            iface: {},
            showprivatekey: "password",
            showpresharedkey: "password",
        }
    },
    mounted: function(){
        var vm = this

        this.axios.get("/serverwg/") // 之后添加参数，让其他只请求server id 和 接口名
        .then(function(res){
            if(res.data.code == 0){
                vm.wgs = res.data.data
                if(vm.wgs.length > 0){
                    vm.serverid = vm.wgs[0].id
                }
            }else{
                vm.prompt = "获取server接口失败！"
            }
        },function(res){
            vm.prompt = "服务端口出错！"
        })

        if(eventbus.e == 'client-add'){
            vm.op = "添加"
        }else if(eventbus.e == 'client-change'){
            vm.serverid = eventbus.data.serverid
            vm.iface = eventbus.data.ifaceinfo
            vm.op = "修改"
        }

    },
    methods: {
        add: function(iface){
            var vm = this
            iface.serverid = this.serverid
            this.axios.post("/clientwg/", iface)
            .then(function(res){
                if(res.data.code == 0){
                    eventbus.$emit("event-change", "client-list-delete")
                }else{
                    vm.prompt = res.data.msg
                }
            },
            function(res){
                vm.prompt = "服务端出错！"
            })
        },
        change: function(iface){
            var vm = this
            this.axios.put("clientwg/", iface)
            .then(function(res){
                if(res.data.code == 0){
                    eventbus.$emit("event-change", "client-list-delete")
                }else{
                    vm.prompt = res.data.msg
                }
            },function(res){
                vm.prompt = "服务端出错！"
            })
            
        },
        select: function(event){
            console.log("event:", event.target.value)
            this.serverid = event.target.value
            console.log("serverid: ", this.serverid)
        },
        show: function(who, arg){
            console.log("who:", who, "arg:", arg)
            if(who == "showprivatekey"){
                if(this.showprivatekey == "text"){
                    this.showprivatekey = "password"
                }else{
                    this.showprivatekey = "text"
                }
            }else if(who == "showpresharedkey"){
                if(this.showpresharedkey == "text"){
                    this.showpresharedkey = "password"
                }else{
                    this.showpresharedkey = "text"
                }
            }
        }
    }
}
</script>