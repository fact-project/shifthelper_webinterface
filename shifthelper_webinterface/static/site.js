var ReactCSSTransitionGroup = React.addons.CSSTransitionGroup;
var update = React.addons.update;
var events = new Events();

var socket = io();

const e = React.createElement;


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

  // filter alerts by category
  filterCategory(element, index, array) {
    if (this.props.categoryFilter == "all") {
      return true;
    } else if (this.props.categoryFilter == "expert") {
      return element.category == "developer" || element.category == "check_error";
    } else {
      return element.category == this.props.categoryFilter;
    }
  },

  render() {
    var alertTable = this.state.alerts.filter(this.filterCategory).map((function(_this){
      return function(alert, i) {
        return e(Alert, {
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
    return e(
      ReactCSSTransitionGroup,
      {
        "transitionName": "alerts",
        "component": "ul",
        "id": "alerts-table",
        "key": alertTable == 0 ? null : alertTable[0].props.uuid,
        "className": "list-group"
      },
      alertTable,
    );
  }
});

var Alert = React.createClass({
  render: function() {
    var button;
    if (this.props.acknowledged === false){
      button = e(
        "button",
        {
          className: "btn btn-danger btn-sm",
          "onClick": this.props.acknowledgeAlert
        },
        "Acknowledge"
      );
    } else {
      button = e(
        "button", {"className": "btn btn-success btn-sm disabled"}, "Done"
      );
    }
    return e(
      "li",
      {"className": "list-group-item clearfix", "style": {"vertical-align": "middle"}, key: this.props.uuid},
      e("div", {"className": "row"},
        e(
          "div", {"className": "col-md-3 col-xs-6 date"},
          this.props.timestamp.format('YYYY-MM-DD HH:mm:ss')
        ),
        e("div", {"className": "col-md-2 col-xs-6 check"}, this.props.check),
        e("div", {"className": "col-md-1 col-xs-6 level"}, this.props.level),
        e("div", {"className": "col-md-4 col-xs-12"}, this.props.text),
        e("div", {"className": "col-md-2 col-xs-6 text-right pull-right"}, button)
      )
    );
  }
});


var AlertsPanel = React.createClass({
  getInitialState: function() {
    return {categoryFilter: "shifter"};
  },
  handleFilterChange: function(event) {
    this.setState({categoryFilter: event.target.value});
  },
  render: function() {
    return e(
      "div",
      {"className": "panel panel-default"},
      e(
        "div",
        {"className": "panel-heading"},
        e(
          'div',
          {"className": "row"},
          e(
            "div",
            {"className": "col-xs-8"},
            e("h3", { "className": "panel-title" }, "Current Alerts")
          ),
          e(
            "div",
            {"className": "col-xs-4 text-right"},
            e(
              "form",
              {"action":"/", "className": "form-inline"},
              e(
                "div",
                {"className": "form-group"},
                e(
                  "select",
                  {
                    "onChange": this.handleFilterChange,
                    "type": "submit",
                    "name": "showAlerts",
                    "className": "form-control",
                    "selected": this.props.categoryFilter
                  },
                  e("option", {"value": "shifter"}, "Shifter"),
                  e("option", {"value": "expert"}, "Expert"),
                  e("option", {"value": "all"}, "All")
                )
              )
            )
          )
        )
      ),
      e(Alerts, {categoryFilter: this.state.categoryFilter})
    );
  }
});

React.render(
  e(
    AlertsPanel,
    null
  ),
  document.getElementById('alerts-panel')
);
