<template>
  <div id="center" class="show">

    <div id="leftmenu" class="show" v-if="this.superuser">
        <label v-on:click="serverwg"><u>Server WireGuard</u></label>
        <br>
        <label v-on:click="myinterfaces"><u>My WireGuard</u></label>
    </div>

    <div id="context" class="show">
      <h3>{{ msg }}</h3>
      <u>
        <li v-for="iface in ifaces">
          <span>{{ iface.name }}</span><span>Allowed-ips: {{ iface.allowedips }}</span><span>{{ iface.comment }}</span><span v-on:click="conf(iface.name)">下载配置</span>
        </li>
      </u>
    </div>

  </div>
</template>


<script>
export default {
  name: "center",
    data: function(){
        return {
            msg: '连接信息',
            superuser: null,
            ifaces: '',
        }
    },
    mounted: function(){
        var vm = this
        this.axios.get("/myinterfaces")
        .then(function(res){
          if(res.data.code == 0){
            vm.ls = res.data
          }else{

          }
        })
    },
    methods:{
        serverwg: function(){
            this.$router.push({path: "/serverwg"})
        },
        myinterfaces: function(){
            this.$router.push({path: "/myinterfaces"})
        },
        conf: function(iface){
          this.axios.get("")
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
  width: 100%;
}

</style>