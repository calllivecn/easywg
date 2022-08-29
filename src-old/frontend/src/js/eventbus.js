import Vue from 'vue'

const eventbus = new Vue()
eventbus.e = ""
eventbus.data = {}
eventbus.etype = function(e, data){
    eventbus.e = e
    eventbus.data = data
}

export default eventbus