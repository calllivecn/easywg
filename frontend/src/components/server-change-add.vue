<template>
    <div>
        <p>{{prompt}}</p>

        <span>接口名：</span><input v-model="iface" placeholder="使用默认接口名">
        <br>

        <span>network: </span><input v-model="net" type="text" placeholder="请输入接口使用的网络地址">
        <br>

        <span>privatekey: </span>
        <input v-model="privatekey" v-bind:type="showprivatekey" placeholder="请输入接口使用的网络地址">
        <button v-on:click="changeprivatekey">显示私钥</button>
        <br>

        <span>publickey: </span><input v-model="publickey" type="text" placeholder="一般不用输入">
        <br>

        <span>listenport: </span><input v-model="listenport" type="text" placeholder="接口端口">
        <br>

        <span>心跳时间: </span><input v-model="persistentkeepalive" type="text" placeholder="35">
        <br>

        <span>是否开机启动: </span><input v-model="boot" type="checkbox">
        <span>{{boot}}</span>
        <br>

        <span>描述：</span>
        <textarea v-model="comment" placeholder="添加一个简短的描述"></textarea>
        <br>
        <button @click="submit">添加接口</button>
    </div>
</template>


<script>
export default {
    name: "server-change-add",
    data: function(){
        return {
            prompt: "",
            showprivatekey: "password",
            iface: null,
            net: null,
            privatekey: null,
            publickey: null,
            listenport: null,
            persistentkeepalive: 35,
            boot: true,
            comment: null,
        }
    },
    methods:{
        changeprivatekey: function(){
            if(this.showprivatekey == "text"){
                this.showprivatekey = "password"
            }else{
                this.showprivatekey = "text"
            }
        },
        submit:function(){
            if(this.net == ""){
                this.prompt = "network 是必填项!"
            }else{
                var vm = this
                this.axios.post("/serverwg/", {
                    "iface": this.iface,
                    "net": this.net,
                    "privatekey": this.privatekey,
                    "listenport": this.listenport,
                    "persistentkeepalive": this.persistentkeepalive,
                    "boot": this.boot,
                    "comment": this.comment,
                })
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
}
</script>