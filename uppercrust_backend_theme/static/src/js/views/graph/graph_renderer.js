odoo.define('uppercrust_backend_theme.GraphRenderer', function (require) {
    "use strict";

    var GraphRenderer = require('web.GraphRenderer');
    var config = require('web.config');
    var core = require('web.core');
    var field_utils = require('web.field_utils');

    var _t = core._t;
    var qweb = core.qweb;

    // hide top legend when too many items for device size
    var MAX_LEGEND_LENGTH = 25 * (1 + config.device.size_class);

    return GraphRenderer.include({
        start: function () {
            var self = this;
            this.theme_colors = [];
        },
        _fetchThemeColors: function () {
            var self = this;
            return self._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['uppercrust_backend_theme.selected_theme']
            }).then(function (theme_id) {
                return self._rpc({
                    model: 'ir.web.theme',
                    method: 'search_read',
                    domain: [['id', '=', parseInt(theme_id)]],
                    fields: ['leftbar_color', 'buttons_color', 'tag_info',
                        'tag_danger', 'tag_success', 'tag_warning',
                        'tag_primary', 'tag_muted'],
                }).then(function (result) {
                    self.theme_colors.push(result[0].buttons_color, result[0].leftbar_color, result[0].tag_info, result[0].tag_danger,
                            result[0].tag_success, result[0].tag_warning, result[0].tag_primary, result[0].tag_muted)
                    // delete result[0].id;
                    // self.theme_colors = _.values(result[0]);
                });
            });
        },
        _renderGraph: function () {
            var self = this;
            this.$el.empty();
            this._fetchThemeColors().then(function () {
                var chart = self['_render' + _.str.capitalize(self.state.mode) + 'Chart']();
                if (chart && chart.tooltip.chartContainer) {
                    self.to_remove = chart.update;
                    nv.utils.onWindowResize(chart.update);
                    chart.tooltip.chartContainer(self.el);
                }
            });
        },
        _processColors: function (n_elements) {
            return this.theme_colors;
        },
        _renderBarChart: function () {
            // prepare data for bar chart
            var self = this;
            var data, values;
            var measure = this.state.fields[this.state.measure].string;

            // zero groupbys
            if (this.state.groupedBy.length === 0) {
                data = [{
                    values: [{
                        x: measure,
                        y: this.state.data[0].value
                    }],
                    key: measure
                }];
            }
            // one groupby
            if (this.state.groupedBy.length === 1) {
                values = this.state.data.map(function (datapt) {
                    return {x: datapt.labels, y: datapt.value};
                });
                data = [
                    {
                        values: values,
                        key: measure,
                    }
                ];
            }
            if (this.state.groupedBy.length > 1) {
                var xlabels = [],
                        series = [],
                        label, serie, value;
                values = {};
                for (var i = 0; i < this.state.data.length; i++) {
                    label = this.state.data[i].labels[0];
                    serie = this.state.data[i].labels[1];
                    value = this.state.data[i].value;
                    if ((!xlabels.length) || (xlabels[xlabels.length - 1] !== label)) {
                        xlabels.push(label);
                    }
                    series.push(this.state.data[i].labels[1]);
                    if (!(serie in values)) {
                        values[serie] = {};
                    }
                    values[serie][label] = this.state.data[i].value;
                }
                series = _.uniq(series);
                data = [];
                var current_serie, j;
                for (i = 0; i < series.length; i++) {
                    current_serie = {values: [], key: series[i]};
                    for (j = 0; j < xlabels.length; j++) {
                        current_serie.values.push({
                            x: xlabels[j],
                            y: values[series[i]][xlabels[j]] || 0,
                        });
                    }
                    data.push(current_serie);
                }
            }
            var svg = d3.select(this.$el[0]).append('svg');
            svg.datum(data);

            svg.transition().duration(0);

            var colors = this._processColors(this.state.data.length);
            var chart = nv.models.multiBarChart();
            chart.options({
                margin: {left: 80, bottom: 100, top: 80, right: 0},
                delay: 100,
                transition: 10,
                showLegend: _.size(data) <= MAX_LEGEND_LENGTH,
                showXAxis: true,
                showYAxis: true,
                rightAlignYAxis: false,
                stacked: this.stacked,
                reduceXTicks: false,
                rotateLabels: -20,
                color: colors,
                showControls: (this.state.groupedBy.length > 1)
            });
            chart.yAxis.tickFormat(function (d) {
                var measure_field = self.state.fields[self.measure];
                return field_utils.format.float(d, {
                    digits: measure_field && measure_field.digits || [69, 2],
                });
            });

            chart(svg);
            return chart;
        },
        _renderPieChart: function () {
            var data = [];
            var all_negative = true;
            var some_negative = false;
            var all_zero = true;

            this.state.data.forEach(function (datapt) {
                all_negative = all_negative && (datapt.value < 0);
                some_negative = some_negative || (datapt.value < 0);
                all_zero = all_zero && (datapt.value === 0);
            });
            if (some_negative && !all_negative) {
                this.$el.append(qweb.render('GraphView.error', {
                    title: _t("Invalid data"),
                    description: _t("Pie chart cannot mix positive and negative numbers. " +
                            "Try to change your domain to only display positive results"),
                }));
                return;
            }
            if (all_zero) {
                this.$el.append(qweb.render('GraphView.error', {
                    title: _t("Invalid data"),
                    description: _t("Pie chart cannot display all zero numbers.. " +
                            "Try to change your domain to display positive results"),
                }));
                return;
            }
            if (this.state.groupedBy.length) {
                data = this.state.data.map(function (datapt) {
                    return {x: datapt.labels.join("/"), y: datapt.value};
                });
            }
            var svg = d3.select(this.$el[0]).append('svg');
            svg.datum(data);

            svg.transition().duration(100);

            var legend_right = config.device.size_class > config.device.SIZES.XS;

            var colors = this._processColors(this.state.data.length);
            var chart = nv.models.pieChart().labelType('percent');
            chart.options({
                delay: 250,
                showLegend: legend_right || _.size(data) <= MAX_LEGEND_LENGTH,
                legendPosition: legend_right ? 'right' : 'top',
                transition: 100,
                color: colors,
            });

            chart(svg);
            return chart;
        },
        _renderLineChart: function () {
            if (this.state.data.length < 2) {
                this.$el.append(qweb.render('GraphView.error', {
                    title: _t("Not enough data points"),
                    description: "You need at least two data points to display a line chart."
                }));
                return;
            }
            var self = this;
            var data = [];
            var tickValues;
            var tickFormat;
            var measure = this.state.fields[this.state.measure].string;

            if (this.state.groupedBy.length === 1) {
                var values = this.state.data.map(function (datapt, index) {
                    return {x: index, y: datapt.value};
                });
                data = [
                    {
                        values: values,
                        key: measure,
                        area: true,
                    }
                ];
                tickValues = this.state.data.map(function (d, i) {
                    return i;
                });
                tickFormat = function (d) {
                    return self.state.data[d].labels;
                };
            }
            if (this.state.groupedBy.length > 1) {
                data = [];
                var data_dict = {};
                var tick = 0;
                var tickLabels = [];
                var serie, tickLabel;
                var identity = function (p) {
                    return p;
                };
                tickValues = [];
                for (var i = 0; i < this.state.data.length; i++) {
                    if (this.state.data[i].labels[0] !== tickLabel) {
                        tickLabel = this.state.data[i].labels[0];
                        tickValues.push(tick);
                        tickLabels.push(tickLabel);
                        tick++;
                    }
                    serie = this.state.data[i].labels[1];
                    if (!data_dict[serie]) {
                        data_dict[serie] = {
                            values: [],
                            key: serie,
                            area: true,
                        };
                    }
                    data_dict[serie].values.push({
                        x: tick, y: this.state.data[i].value,
                    });
                    data = _.map(data_dict, identity);
                }
                tickFormat = function (d) {
                    return tickLabels[d];
                };
            }

            var svg = d3.select(this.$el[0]).append('svg');
            svg.datum(data);

            svg.transition().duration(0);


            var colors = this._processColors(this.state.data.length);
            var chart = nv.models.lineChart();
            chart.options({
                margin: {left: 80, bottom: 100, top: 80, right: 0},
                useInteractiveGuideline: true,
                showLegend: _.size(data) <= MAX_LEGEND_LENGTH,
                showXAxis: true,
                showYAxis: true,
                color: colors,
            });
            chart.xAxis.tickValues(tickValues)
                    .tickFormat(tickFormat);
            chart.yAxis.tickFormat(function (d) {
                return field_utils.format.float(d, {
                    digits: self.state.fields[self.state.measure] && self.state.fields[self.state.measure].digits || [69, 2],
                });
            });

            chart(svg);
            return chart;
        },
    });

});
