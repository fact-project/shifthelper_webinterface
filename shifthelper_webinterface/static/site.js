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
    heartbeats: {'shifthelperHeartbeat': 0, 'heartbeatMonitor': 0},
    heartbeatOutdated: {'shifthelperHeartbeat': true, 'heartbeatMonitor': true},
    categoryFilter: 'shifter'
  },
  methods: {
    getAlerts: function() {
      $.getJSON('/alerts', (alerts) => {this.alerts = alerts;});
    },
    getHeartbeats: function() {
      $.getJSON('/heartbeats', (heartbeats) => {
        this.heartbeats = heartbeats;
        this.checkHeartbeatOutdated();
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
    checkHeartbeatOutdated: function() {
      for (var key in this.heartbeats) {
        ts = moment(this.heartbeats[key]).utc();
        diff = moment().utc().diff(ts.utc());
        this.heartbeatOutdated[key] = diff > (1000 * 60 * 1);
      }
      console.log(Object.assign({}, this.heartbeatOutdated));
    }
  },
  computed: {
    filteredAlerts: function() {
      return this.alerts.filter((alert) => {
        if (this.categoryFilter == "all") {
        return true;
        } else if (this.categoryFilter == "expert") {
          return alert.category == "developer" || alert.category == "check_error";
        } else {
          return alert.category == this.categoryFilter;
        }
      });
    }
  },
  mounted: function() {
    this.checkHeartbeatOutdated();
    setInterval(this.checkHeartbeatOutdated, 10000);
  }
})

app.getAlerts();
app.getHeartbeats();
socket.on('updateAlerts', app.getAlerts);
socket.on('updateHeartbeats', app.getHeartbeats);
