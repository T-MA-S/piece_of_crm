// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
	// *     example: number_format(1234.56, 2, ',', ' ');
	// *     return: '1 234,56'
	number = (number + '').replace(',', '').replace(' ', '');
	var n = !isFinite(+number) ? 0 : +number,
		prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
		sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
		dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
		s = '',
		toFixedFix = function (n, prec) {
			var k = Math.pow(10, prec);
			return '' + Math.round(n * k) / k;
		};
	// Fix for IE parseFloat(0.55).toFixed(0) = 0;
	s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
	if (s[0].length > 3) {
		s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
	}
	if ((s[1] || '').length < prec) {
		s[1] = s[1] || '';
		s[1] += new Array(prec - s[1].length + 1).join('0');
	}
	return s.join(dec);
}


async function create_chart(array, statuses, all_count, currency) {
	$('#myBarChart').remove();
	$(".chart-bar-1").append('<canvas id="myBarChart"><canvas>');
	var ctx = document.getElementById("myBarChart");
	var myBarChart = new Chart(ctx, {
		type: 'bar',
		data: {
			labels: Object.keys(statuses),
			datasets: [{
				label: gettext("Total"),
				backgroundColor: "#4e73df",
				hoverBackgroundColor: "#2e59d9",
				borderColor: "#4e73df",
				data: array,
			}],
		},
		options: {
			maintainAspectRatio: false,
			layout: {
				padding: {
					left: 10,
					right: 25,
					top: 25,
					bottom: 0
				}
			},
			scales: {
				xAxes: [{
					time: {
						unit: 'month'
					},
					gridLines: {
						display: false,
						drawBorder: false
					},
					ticks: {
						maxTicksLimit: 20,
					},
					maxBarThickness: 50,
				}],
				yAxes: [{
					ticks: {
						min: 0,
						maxTicksLimit: 5,
						padding: 10,
						// Include a dollar sign in the ticks
						callback: function (value, index, values) {
							return number_format(value) + " " + currency;
						}
					},
					gridLines: {
						color: "rgb(234, 236, 244)",
						zeroLineColor: "rgb(234, 236, 244)",
						drawBorder: false,
						borderDash: [2],
						zeroLineBorderDash: [2]
					}
				}],
			},
			legend: {
				display: false
			},
			tooltips: {
				titleMarginBottom: 10,
				titleFontColor: '#6e707e',
				titleFontSize: 14,
				backgroundColor: "rgb(255,255,255)",
				bodyFontColor: "#858796",
				borderColor: '#dddfeb',
				borderWidth: 1,
				xPadding: 15,
				yPadding: 15,
				displayColors: false,
				caretPadding: 10,
				callbacks: {
					label: function (tooltipItem, chart) {
						var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
						return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
					}
				}
			},
		}
	});
}


async function create_piechart_1(data, statuses) {
	$('#BarPieChart-1').remove();
	$(".chart-bar-2").html("");
	$(".chart-bar-2").append('<canvas id="BarPieChart-1"><canvas>');
	var ctx = $("#BarPieChart-1");
	var myLineChart = new Chart(ctx, {
		type: 'doughnut',
		data: {
			labels: Object.keys(statuses),
			datasets: [{
				data: data,
				backgroundColor: Object.values(statuses)
			}]
		},
		options: {
			legend: {
				display: false
			},
		}
	});
}

async function create_piechart_2(data, statuses) {
	$('#BarPieChart-2').remove();
	$(".chart-bar-3").append('<canvas id="BarPieChart-2"><canvas>');
	var ctx = $("#BarPieChart-2");
	var myLineChart = new Chart(ctx, {
		type: 'doughnut',
		data: {
			labels: Object.keys(statuses),
			datasets: [{
				data: data,
				backgroundColor: Object.values(statuses)
			}]
		},
		options: {
			legend: {
				display: false
			},
		}
	});
}

async function update_stats_table(url, board_id, currency_id) {
	$.ajax({
		url: url,
		type: 'GET',
		data: {
			board_id: board_id,
			currency_id: currency_id
		},
		success: function (resposne) {
			document.getElementById("stats_table_block").innerHTML = resposne;
		},
		error: function (xhr) {
			document.getElementById("stats_table_block").innerHTML = ''
			alert("something wrong!");
		}
	});
}

async function change_currency(url, update_stats_table_url) {
	var board_id = $("#boards").val();
	var currency_id = $("#currency").val();
	var board_member_id = $("#board_members").val();

	$.ajax({
		url: url,
		type: "get", //send it through get method
		data: {
			board_id: board_id,
			currency_id: currency_id,
			board_member_id: board_member_id,
		},
		success: function (response) {

			create_chart(response['data'], response['statuses'], response['common_sum'], response['currency']);
			create_piechart_1(response['data'], response['statuses']);
			create_piechart_2(response['data'], response['statuses']);
			update_stats_table(update_stats_table_url, board_id, currency_id);

		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});


}

function piechart_update(period, url) {
	var hours = 0;
	var period_from = 0;
	var period_to = 0;

	if (period == 'last_24') hours = 24;
	else if (period == 'last_48') hours = 48;
	else if (period == 'last_week') hours = 168;
	else if (period == 'last_month') hours = 744;
	else if (period == 'custom') {
		var period_to = document.getElementById("period_to");
		period_to.valueAsDate = new Date();
		period_to.max = new Date();
		return
	}
	else if (period == 'custom_form') {
		period_from = document.getElementById('period_from').value;
		period_to = document.getElementById('period_to').value;
	}

	var board_id = $("#boards").val();
	var currency_id = $("#currency").val();
	var board_member_id = $("#board_members").val();

	$.ajax({
		url: url,
		type: "get",
		data: {
			board_id: board_id,
			currency_id: currency_id,
			board_member_id: board_member_id,
			hours: hours,
			period_from: period_from,
			period_to: period_to
		},
		success: function (response) {
			var data = response['data'];
			if (!data) {
				document.getElementById("custom-period-block").innerHTML = gettext('During this period, the status of transactions did not change');
			} else create_piechart_1(response['data'], response['statuses']);
		},
		error: function (xhr) {
			alert("something wrong!");
		}
	});
}


function custom_periodform_submit(e, period, url) {
	e.preventDefault();
	piechart_update(period, url);
	$('#custom_filter').modal('hide');
}