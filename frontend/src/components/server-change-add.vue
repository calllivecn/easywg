<template>
    <div>
        <p>{{prompt}}</p>

        <span>接口名：</span><input v-model="iface.iface" placeholder="留空使用默认接口名">
        <br>

        <span>network: </span><input v-model="iface.net" type="text" placeholder="网络地址">
        <br>

        <span>privatekey: </span>
        <input v-model="iface.privatekey" v-bind:type="showprivatekey" placeholder="私钥(留空为自动生成)">
        <button v-on:click="show_privatekey">显示私钥</button>
        <br>

        <span>publickey: </span><input v-model="iface.publickey" type="text" placeholder="一般不用输入">
        <br>

        <span>listenport: </span><input v-model="iface.listenport" type="text" placeholder="端口(留空自动生成)">
        <br>

        <span>心跳时间: </span><input v-model="iface.persistentkeepalive" type="text" placeholder="35">
        <br>

        <span>是否开机启动: </span><input v-model="iface.boot" type="checkbox">
        <br>

        <span>描述：</span>
        <textarea v-model="iface.comment" placeholder="添加一个简短的描述"></textarea>
        <br>
        <button v-if="op == '添加'" v-on:click="add">{{ op }}</button>
        <button v-if="op == '修改'" v-on:click="change">{{ op }}</button>
    </div>
</template>


<script>
export default {
    name: "server-change-add",
    props: ['ifaceinfo'],
    data: function(){
        return {
            prompt: "",
            showprivatekey: "password",
            op: "添加", // or 修改
            iface: {},
        }
    },
    mounted:function(){
        if(this.ifaceinfo == 'S_ADD'){
            this.iface = {boot: true}
        }else{
            this.iface = this.ifaceinfo
            this.op = "修改"
        }
    },
    methods:{
        show_privatekey: function(){
            if(this.showprivatekey == "text"){
                this.showprivatekey = "password"
            }else{
                this.showprivatekey = "text"
            }
        },
        add: function(){
            if(this.net == ""){
                this.prompt = "network 是必填项!"
            }else{
                var vm = this
                this.axios.post("/serverwg/", this.iface)
                .then(function(res){
                    if(res.data.code == 0){
                        vm.$emit("server-list", vm.iface)
                    }else{
                        vm.prompt = res.data.msg
                    }
                },function(){
                    vm.prompt = "服务端出错!"
                })
            }
        },
        change: function(){
                var vm = this
                this.axios.put("/serverwg/", this.iface)
                .then(function(res){
                    if(res.data.code == 0){
                        vm.$emit("server-list")
                    }else{
                        vm.prompt = res.data.msg
                    }
                },function(){
                    vm.prompt = "服务端出错!"
                })

        }
    }
}
</script>