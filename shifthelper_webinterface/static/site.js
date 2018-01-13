"use strict;"


var socket = io();

function convertLevelToString (level) {
  var str;
  switch(level){
    case 10: str = 'DEBUG'; break;
    case 20: str = 'INFO'; break;
    case 30: str = 'WARNING'; break;
    case 40: str = 'ERROR'; break;
    case 50: str = 'CRITICAL'; break;
    default: str = level.toString();
  }
  return str;
}

function errorMessage(msg) {
  div = $('<div>', {"class": 'alert alert-danger alert-dismissable'});
  div.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>');
  div.append($('<strong>').text(msg));
  return $('#alerts-panel').before(div);
}

app = new Vue({
  el: '#app',
  delimiters: ['((', '))'],
  data: {
    msg: 'Hello World',
    alerts: [],
    heartbeats: {'shifthelperHeartbeat': '', 'heartbeatMonitor': ''},
    categoryFilter: 'shifter'
  },
  methods: {
    getAlerts: function() {
      $.getJSON('/alerts', (alerts) => {this.alerts = alerts;});
    },
    getHeartbeats: function() {
      $.getJSON('/heartbeats', (heartbeats) => {
        console.log(heartbeats);
        console.log(this);
        this.heartbeats = heartbeats;
      });
    },
    acknowledgeAlert: function(uuid) {
      $.ajax({
        url: "/alerts/" + uuid,
        type: "PUT",
        statusCode: {
          401: () => {errorMessage('You need to login first!');}
          }
      });
    },
  }
})

app.getAlerts();
app.getHeartbeats();
socket.on('updateAlerts', app.getAlerts);
socket.on('updateHeartbeats', app.getHeartbeats);
