from flask import Flask, render_template, request
from py2neo import Graph
import json

app = Flask(__name__)

# graph = Graph('http://localhost:7474',username='neo4j',password='123456')  老版本的py2neo
graph = Graph("http://localhost:7474", auth=("neo4j", "123456"))


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/knowledge2.html', methods=['GET', 'POST'])
def knowledge2():
    ctx = {}
    if request.method == 'POST':
        # 接收前端传过来的查询值
        node_name = request.form.get('node')
        num = request.form.get('num')
        # 查询结果
        search_neo4j_data = search_one(node_name, num)
        # 未查询到该节点
        if search_neo4j_data == 0:
            ctx = {'title': '数据库中暂未添加该实体'}
            return render_template('knowledge2.html', ctx=ctx)
        # 查询到了该节点
        else:
            return render_template('knowledge2.html', search_neo4j_data=search_neo4j_data, ctx=ctx)
    return render_template('knowledge2.html', ctx=ctx)



@app.route('/friends_rel_kg/', methods=['GET', 'POST'])
def friends_rel_kg():
    ctx = {}
    if request.method == 'POST':
        # 接收前端传过来的查询值
        node_name = request.form.get('node')
        num = request.form.get('num')
        # 查询结果
        search_neo4j_data = search_one(node_name, num)
        # 未查询到该节点
        if search_neo4j_data == 0:
            ctx = {'title': '数据库中暂未添加该实体'}
            return render_template('friends_rel_kg.html', ctx=ctx)
        # 查询到了该节点
        else:
            return render_template('friends_rel_kg.html', search_neo4j_data=search_neo4j_data, ctx=ctx)
    return render_template('friends_rel_kg.html', ctx=ctx)


@app.route('/knowledge.html', methods=['GET', 'POST'])
def data_show():
    return render_template('knowledge.html')


@app.route('/search_name', methods=['GET', 'POST'])
def search_node():
    # 获取前端传来的变量
    name = request.args.get('name')
    num = request.args.get('num')
    if num == '':
        num = 10
    json_data = query(str(name), int(num))
    return json_data


# 知识点查询
def query(name, num):
    # data = graph.run("MATCH p=(n{name:'%s'})--() RETURN p LIMIT 25" % name).data()
    # cql = "match p=(n1)-[r]-(n2) where (n1.name =~ '.*%s.*') return n1,r,n2 limit %s" % (name, num)
    cql = "match p=(n1)-[r]-(n2) return n1,r,n2 limit %s" % (num)
    cql = "match p=(n1)<-[r:`好友`]-(n2) return n1,r,n2 limit %s " \
          "union" \
          " match p=(n1)-[r:`朝代`]-(n2) return n1,r,n2 limit 20 " \
          "union" \
          " match p=(n1)-[r:`包含`]-(n2) return n1,r,n2 limit %s" % (num, num)

    # 创建一个nodes列表存储节点信息
    nodes = []
    # 创建一个links列表存储关系信息
    links = []
    # 创建一个categories列表存储标签信息
    categories = []
    # 创建一个nodes id 列表，记录nodes id，防止nodes列表中存储重复节点
    nodes_id = []

    results = graph.run(cql).data()
    # print(results)
    for result in results:
        # 开始节点添加label、id属性
        # 设置name属性防止重复，name属性值设为id值
        # result['r'].start_node.clear()

        if result['r'].start_node.identity not in nodes_id:
            nodes_id.append(result['r'].start_node.identity)
            result['r'].start_node['label'] = list(result['r'].start_node.labels)[0]
            result['r'].start_node['id'] = str(result['r'].start_node.identity)

            # 把开始节点、结束节点放入nodes列表
            nodes.append(result['r'].start_node)

        if result['r'].end_node.identity not in nodes_id:
            nodes_id.append(result['r'].end_node.identity)
            result['r'].end_node['label'] = list(result['r'].end_node.labels)[0]
            result['r'].end_node['id'] = str(result['r'].end_node.identity)

            # 把开始节点、结束节点放入nodes列表
            nodes.append(result['r'].end_node)

        # 创建一个关系字典
        link = {'source': str(result['r'].start_node.identity),
                'target': str(result['r'].end_node.identity),
                'type': list(result['r'].types())[0],
                'id': str(result['r'].identity),
                }
        # 把关系link放入links列表
        links.append(link)

        # 获取两个节点的标签，如果标签不在categories列表里就放入进去
        labels = list(result['r'].labels())
        for label in labels:
            if label not in categories:
                categories.append(label)

    # 给节点添加category属性，方便前端图例使用
    for i in range(len(nodes)):
        nodes[i]['category'] = categories.index(nodes[i]['label'])

    # 给category添加name属性，方便前端直接使用
    for i in range(len(categories)):
        categories[i] = {
            'name': categories[i]
        }

    # 创建一个datas字典
    datas = {"nodes": nodes,
             "links": links,
             "categories": categories,
             }
    # 把datas字典转化成json数据
    datas_json = json.dumps(datas, ensure_ascii=False)
    # print("query_data:", data)
    return datas_json



def search_one(value, num):
    # 定义data数组存储节点信息
    data = []
    # 定义links数组存储关系信息
    links = []
    # 查询节点是否存在
    node = graph.run('MATCH(n{name:"' + value + '"}) return n').data()
    # 如果节点存在len(node)的值为1不存在的话len(node)的值为0
    if len(node):
        # 如果该节点存在将该节点存入data数组中
        # 构造字典存放节点信息
        dict = {
            'name': value,
            'symbolSize': 50,
            'category': '作者'
        }
        data.append(dict)
        num = str(num)
        # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
        # nodes = graph.run('MATCH(n:author{name:"' + value + '"})<-->(m:author) return m').data()
        nodes = graph.run('MATCH(n{name:"' + value + '"})<-->(m) return m limit ' + num + '').data()
        # MATCH(n:author{name:"文天祥"})<-->(m:author) return m
        # 查询该节点所涉及的所有relationship，无向，步长为1，并返回这些relationship
        reps = graph.run('MATCH(n{name:"' + value + '"})<-[rel]->(m) return rel limit ' + num + '').data()
        # 处理节点信息
        name_ls = []
        for n in nodes:
            # 将节点信息的格式转化为json
            node = json.dumps(n, ensure_ascii=False)
            node = json.loads(node)
            # 取出节点信息中person的name
            name = str(node['m']['name'])
            if name not in name_ls:
                name_ls.append(name)
            else:
                continue
            # 构造字典存放单个节点信息
            dict = {
                'name': name,
                'symbolSize': 50,
                'category': '作者'
            }
            # 将单个节点信息存储进data数组中
            data.append(dict)
        # 处理relationship
        for r in reps:
            source = str(r['rel'].start_node['name'])
            target = str(r['rel'].end_node['name'])
            name = str(type(r['rel']).__name__)
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            links.append(dict)
        # 构造字典存储data和links
        search_neo4j_data = {
            'data': data,
            'links': links
        }
        # 将dict转化为json格式
        search_neo4j_data = json.dumps(search_neo4j_data)
        return search_neo4j_data
    else:
        print("查无此人")
        return 0


if __name__ == '__main__':
    app.run(debug=True)
