<template>
    <div>
        <header>Server 接口信息</header>
        <p>{{ prompt }}</p>
        <button v-on:click="serveradd">添加</button>
            
        <table>
            <tr>
              <th>Server 接口</th>
              <th>网络和地址</th>
              <th>公钥</th>
              <th>自启动</th>
              <th>描述</th>
              <th>配置</th>
            </tr>
            <tr v-for="iface in data" v-bind:key="iface.iface" >
              <td>{{ iface.iface }}</td>
              <td>{{ iface.net }}</td>
              <td>{{ iface.publickey }}</td>
              <td>{{ iface.boot }}</td>
              <td>{{ iface.comment }}</td>
              <td v-on:click="change(iface.iface)">修改</td>
              <td v-on:click="remove(iface.iface)">删除</td>
            </tr>
        </table>
    </div>
</template>


<script>
import eventbus from '../js/eventbus.js'

export default {
    name: "server-list-delete",
    data(){
        return {
            prompt: "",
            data: [],
        }
    },
    created: function(){
        console.log("server-list-delte created")
    },
    mounted: function(){
        console.log("server-list-delte mounted")
        var vm = this
        this.axios.get("/serverwg/")
        .then(function(res){
            if(res.data.code == 0){
              vm.data = res.data.data
              //vm.$Message.info("请求成功。")
              console.log("请求成功。")
            }else{
              //vm.$Message.info("接口出现问题。")
              console.log("接口出现问题:", res.data.msg)
            }
        },
        function(res){
          console.log("服务器出错")
          //vm.$message("服务器出错")
        })
    },
    methods:{
        serveradd: function(){
            console.log("server 添加")
            this.$emit('server-add')
        },
        change:function(iface){
            console.log("server 修改: ", iface)
            var vm = this

            this.axios.get("/serverwg/", {params: {"iface": iface}})
            .then(function(res){
                if(res.data.code == 0){
                    vm.$emit("server-change", res.data.data)
                }else{
                    vm.prompt = res.data.msg
                }
            })

        },
        remove: function(iface){
            var vm = this
            var iface_remove = iface

            this.axios.delete("/serverwg/", {data:{
                    "iface": iface
                }
            })
            .then(function(res){
                if(res.data.code == 0){
                    let log = "成功删除接口： " + iface_remove
                    console.log(log)
                    for(const i in vm.data){
                        if(vm.data[i].iface == iface_remove){
                            vm.data.splice(i, 1)
                        }
                    }
                    vm.prompt = log
                }else{
                    vm.prompt = res.data.msg
                }
            },
            function(res){
                vm.prompt = res.data.msg
            })
        }
    }
}
</script>