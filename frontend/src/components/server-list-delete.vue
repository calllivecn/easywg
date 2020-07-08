<template>
    <div>
        <header>Server 接口信息</header>
        <p>{{ prompt }}</p>
        <button v-on:click="add">添加</button>
            
        <table>
            <tr>
              <th>Server 接口</th>
              <th>Address</th>
              <th>端口</th>
              <th>网络地址</th>
              <th>公钥</th>
              <th>自启动</th>
              <th>描述</th>
              <th>配置</th>
            </tr>
            <tr v-for="iface in data" v-bind:key="iface.iface" >
              <td>{{ iface.iface }}</td>
              <td>{{ iface.address}}</td>
              <td>{{ iface.listenport }}</td>
              <td>{{ iface.network }}</td>
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
        var vm = this

        eventbus.$on('event-change', function(e){
            vm.prompt = ""
        })

        eventbus.$on("server-change-data", function(iface){
            for(let i in vm.data){
                if(vm.data[i].id == iface.id){
                    vm.data.splice(i, 1, iface)
                    return
                }
            }
            vm.data.push(iface)
            vm.data.sort(function(a, b){return a.id - b.id})
        })
        
        
        this.axios.get("/serverwg/")
        .then(function(res){
            if(res.data.code == 0){
              vm.data = res.data.data
            }else{
                vm.prompt = res.data.msg
            }
        },
        function(res){
          vm.prompt = "服务器出错！"
        })
    },
    mounted: function(){
    },
    methods:{
        add: function(){
            eventbus.$emit('event-change', 'server-change-add')
            eventbus.$emit('server-change', null)
        },
        change: function(iface){
            console.log("server 修改: ", iface)
            var vm = this

            this.axios.get("/serverwg/", {params: {"iface": iface}})
            .then(function(res){
                if(res.data.code == 0){
                    eventbus.$emit("event-change", "server-change-add")
                    eventbus.$emit("server-change", res.data.data)
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
                vm.prompt = "服务器出错！"
            })
        }
    }
}
</script>