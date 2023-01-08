var myChart = echarts.init(document.getElementById("guanxi"));
$(document).keypress(function (e) {
        // 回车键事件
        if (e.which == 13) {
            var name = $("#search").val();
            var num = $("#search_num").val();
            search(name, num);
        }
    });
    // $("#c_search").click(function () {
    //     var name = $("#search").val();
    //     var num = $("#search_num").val();
    //     alert(name);
    //     search(name, num);
    // })
 function search(name, num) {
        $.getJSON('/search_name', {
                name: name,
                num: num,
            }, function (graph) {
                myChart.hideLoading();
                graph.nodes.forEach(function (node) {
                    node.symbolSize = 30;
                });
                option = {
                    title: {
                        subtext: 'Default layout',
                        top: 'bottom',
                        left: 'right'
                    },
                    tooltip: {
                        show: true,    // 是否显示提示框组件
                        position: [10, 20],
                        extraCssText: 'white-space: pre-wrap; word-break: break-all;',
                        triggerOn: 'click',
                        confine: true,
                        formatter: function (params) {
                            //遍历params.data
                            var str = "";
                            for (var i in params.data) {
                                str += '<span  style=\"display:inline-block;margin-right:5px;border-radius:5px;width:10px;height:10px;background-color:#F56A6A\"></span>' + i + ":" + params.data[i] + "<br>";
                            };
                            str = '<marquee direction="up" onMouseOut=start(); onMouseOver=stop(); behavior="alternate" scrolldelay="10" scrollamount="1"  style=\"width:700px; max-height:400px;overflow-y:auto;\">'+str+'</marquee>';
                            return str;
                        }
                    },
                    legend: [
                        {
                            data: graph.categories.map(function (a) {
                                return a.name;
                            })
                        }
                    ],
                    series: [
                        {
                            name: '医疗诊断知识图谱',
                            type: 'graph',
                            layout: 'force',
                            data: graph.nodes,
                            links: graph.links,
                            categories: graph.categories,
                            roam: true,
                            edgeSymbol: ['circle', 'arrow'],
                            label: {
                                show: true,
                                position: 'inside'
                            },
                            force: {
                                repulsion: 100
                            },
                            edgeLabel: {
                                show: true,
                                position: 'middle',
                                formatter: function (params) {
                                    let str = params.data.type;
                                    return str;
                                }
                            }
                        }
                    ]
                };
                myChart.setOption(option, true);
            }
        );
    }

    //base64转blob
function base64ToBlob(code) {
    let parts = code.split(';base64,');
    let contentType = parts[0].split(':')[1];
    let raw = window.atob(parts[1]);
    let rawLength = raw.length;
    let uInt8Array = new Uint8Array(rawLength);
    for (let i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
    }
    return new Blob([uInt8Array], {type: contentType});
}

function saveAsImage() {
    let content = myChart.getDataURL();

    let aLink = document.createElement('a');
    let blob = this.base64ToBlob(content);

    let evt = document.createEvent("HTMLEvents");
    evt.initEvent("click", true, true);
    aLink.download = "graph.png";
    aLink.href = URL.createObjectURL(blob);
    aLink.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));

    var base64_data = myChart.getDataURL();
    $.getJSON('/base', {
            base: base64_data,
        }
        , function (json) {
        });
}