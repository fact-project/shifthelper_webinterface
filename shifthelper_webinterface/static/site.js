var ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;
var update = React.addons.update;
var events = new Events();

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

var Alerts = React.createClass({

  getInitialState: function() {
    return {alerts: []};
  },

  componentDidMount() {
    $.getJSON('/alerts', this._updateAlerts);
    socket.on('update', this._update);
  },

  _updateAlerts(alerts) {
    return this.setState({alerts: alerts});
  },

  _update(data) {
    var alerts = JSON.parse(data);
    return this.setState({alerts: alerts});
  },

  acknowledgeAlert(uuid) {
    $.ajax({
      url: "/alerts/" + uuid,
      type: "PUT",
      statusCode: {
        401: function() {
          div = $('<div>', {"class": 'alert alert-danger alert-dismissable'});
          div.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>');
          div.append($('<strong>').text('You need to login first!'));
          return $('#alerts-panel').before(div);
        }
      }
    });
  },

  render() {
    var alertTable = this.state.alerts.map((function(_this){
      return function(alert, i) {
        return React.createElement(Alert, {
          "acknowledged": alert.acknowledged,
          "category": alert.category,
          "check": alert.check,
          "level": convertLevelToString(alert.level),
          "text": alert.text,
          "timestamp": moment(alert.timestamp),
          "uuid": alert.uuid,
          "acknowledgeAlert": _this.acknowledgeAlert.bind(_this, alert.uuid)
        });
      };
    })(this));
    return React.createElement(
      ReactCSSTransitionGroup,
      {
        "transitionName": "alerts",
        "component": "ul",
        "id": "alerts-table",
        "className": "list-group"
      },
      alertTable
    );
  }
});

var Alert = React.createClass({
  render: function() {
    var button;
    if (this.props.acknowledged === false){
      button = React.createElement(
        "button",
        {
          className: "btn btn-danger btn-sm",
          "onClick": this.props.acknowledgeAlert
        },
        "Acknowledge"
      );
    } else {
      button = React.createElement(
        "button", {"className": "btn btn-success btn-sm"}, "Done"
      );
    }
    return React.createElement(
      "li",
      {"className": "list-group-item clearfix", "style": {"vertical-align": "middle"}},
      React.createElement("div", {"className": "row"},
        React.createElement(
          "div", {"className": "col-md-3 col-xs-6 date"},
          this.props.timestamp.format('YYYY-MM-DD HH:mm:ss')
        ),
        React.createElement("div", {"className": "col-md-2 col-xs-6 check"}, this.props.check),
        React.createElement("div", {"className": "col-md-1 col-xs-6 level"}, this.props.level),
        React.createElement("div", {"className": "col-md-4 col-xs-12"}, this.props.text),
        React.createElement("div", {"className": "col-md-2 col-xs-6 text-right pull-right"}, button)
      )
    );
  }
});


var AlertsPanel = React.createClass({
  render: function() {
    return React.createElement(
      "div",
      {"className": "panel panel-default"},
      React.createElement(
        "div",
        {"className": "panel-heading"},
        React.createElement("h3", { "className": "panel-title" }, "Current Alerts")
      ),
      React.createElement(Alerts, null)
    );
  }
});


React.render(React.createElement(AlertsPanel, null), document.getElementById('alerts-panel'));
