<template>
  <div id="center" class="show">

    <div id="leftmenu" class="show" v-if="superuser">
        <label v-on:click="serverwg"><u>Server WireGuard</u></label>
        <br>
        <label v-on:click="myinterfaces"><u>My WireGuard</u></label>
    </div>

    <div id="context" class="show something">
      <header class="something">{{ msg }}</header>
      <table v-if="WG == 'C'">
        <tr><th>接口名</th><th>启用的网络</th><th>描述</th><th>conf配置</th></tr>
        <tr v-for="iface in data" v-if="data.length > 0">
          <td>{{ iface.name }}</td>
          <td>Allowed-ips: {{ iface.allowedips }}</td>
          <td>{{ iface.comment }}</td>
          <td v-on:click="conf(iface.name)">下载配置</td>
        </tr>
      </table>

      <table v-if="this.WG == 'S'">
        <tr>
          <th>Server 接口</th>
          <th>网络和地址</th>
          <th>公钥</th>
          <th>自启动</th>
          <th>描述</th>
          <th>配置</th>
        </tr>
        <tr v-for="iface in data" v-if="data.length > 0">
          <td>{{ iface.iface }}</td>
          <td>{{ iface.net }}</td>
          <td>{{ iface.publickey }}</td>
          <td>{{ iface.boot }}</td>
          <td>{{ iface.comment }}</td>
          <td v-on:click="configS(iface.name)">配置</td>
        </tr>
      </table>
    </div>

  </div>
</template>


<script>
export default {
  name: "center",
    data: function(){
        return {
            msg: '',
            superuser: null,
            data: '',
            WG: 'C',
        }
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
        serverwg: function(){

            this.msg = "Server 接口信息"
            this.WG = "S"

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
        myinterfaces: function(){
            this.msg = "peer 信息"
            this.WG = "C"
            var vm = this
            this.axios.get("/myinterfaces/")
            .then(function(res){
              if(res.data.code == 0){
                vm.ifaces = res.data.data
              }else{
                //vm.$Message.info("接口出现问题。")
                console.log("接口出现问题:", res.data.msg)
              }
            })
        },
        conf: function(iface){
          this.axios.get("/")
        }
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