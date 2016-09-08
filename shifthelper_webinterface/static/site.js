var ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;
var update = React.addons.update;
var events = new Events();

var socket = io();

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

  render() {
    var alertTable;
    alertTable = this.state.alerts.map(function(alert, i) {
      return React.createElement(Alert, {
        "acknowledged": alert.acknowledged,
        "category": alert.category,
        "check": alert.check,
        "level": alert.level,
        "text": alert.text,
        "timestamp": alert.timestamp,
        "uuid": alert.uuid
      });
    });
    return React.createElement(
      ReactCSSTransitionGroup,
      {
        "transitionName": "alerts",
        "component": "tbody",
        "id": "alerts-table",
      },
      alertTable
    );
  }
});

var Alert = React.createClass({
  render: function() {
    return React.createElement(
      "tr", {},
      React.createElement('td', null, this.props.timestamp),
      React.createElement('td', null, this.props.check),
      React.createElement('td', null, this.props.level),
      React.createElement('td', null, this.props.text)
    );
  }
});


var AlertsPanel = React.createClass({
  render: function() {
    return React.createElement(
      "div",
      {},
      React.createElement(
        "table", {"className": "pure-table"},
        React.createElement(
          "thead", null,
          React.createElement(
            "tr", null,
            React.createElement("th", null, "TimeStamp"),
            React.createElement("th", null, "Check"),
            React.createElement("th", null, "Level"),
            React.createElement("th", null, "Message")
          )
        ),
        React.createElement(Alerts)
      )
    );
  }
});


React.render(React.createElement(AlertsPanel, null), document.getElementById('alerts-panel'));
