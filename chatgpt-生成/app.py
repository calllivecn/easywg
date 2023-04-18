import os
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

CONFIG_PATH = '/etc/wireguard/wg0.conf'

@app.route('/api/config', methods=['GET'])
def get_config():
    with open(CONFIG_PATH, 'r') as f:
        config = f.read()
    return jsonify({
        'status': 'success',
        'data': config,
    })

@app.route('/api/config', methods=['POST'])
def add_config():
    data = request.json
    if not data or 'config' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid request data',
        }), 400
    config = data['config']
    with open(CONFIG_PATH, 'a') as f:
        f.write(config)
    return jsonify({
        'status': 'success',
        'message': 'Configuration added successfully',
    })

@app.route('/api/config/<int:id>', methods=['PUT'])
def update_config(id):
    data = request.json
    if not data or 'config' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid request data',
        }), 400
    config = data['config']
    with open(CONFIG_PATH, 'r') as f:
        lines = f.readlines()
    if id < 0 or id >= len(lines):
        return jsonify({
            'status': 'error',
            'message': 'Invalid configuration ID',
        }), 400
    lines[id] = config + '\n'
    with open(CONFIG_PATH, 'w') as f:
        f.writelines(lines)
    return jsonify({
        'status': 'success',
        'message': 'Configuration updated successfully',
    })

@app.route('/api/config/<int:id>', methods=['DELETE'])
def delete_config(id):
    with open(CONFIG_PATH, 'r') as f:
        lines = f.readlines()
    if id < 0 or id >= len(lines):
        return jsonify({
            'status': 'error',
            'message': 'Invalid configuration ID',
        }), 400
    del lines[id]
    with open(CONFIG_PATH, 'w') as f:
        f.writelines(lines)
    return jsonify({
        'status': 'success',
        'message': 'Configuration deleted successfully',
    })

if __name__ == '__main__':
    app.run()


"""
在这个示例中，我们使用了Flask框架来编写Python后端应用程序，它可以通过API来处理WireGuard配置的增删改查操作。具体来说，我们定义了以下API路由：

GET /api/config - 获取WireGuard配置列表。
POST /api/config - 添加新的WireGuard配置。
PUT /api/config/<int:id> - 更新现有的WireGuard配置。
DELETE /api/config/<int:id> - 删除现有的WireGuard配置。
在这个示例中，我们使用了这些Flask方法：

Flask() - 创建一个新的Flask应用程序实例。
route() - 将URL路由映射到视图函数。
jsonify() - 返回JSON响应。
request - 包含当前请求的信息和数据的对象。
在这个示例中，我们使用了这些Python方法：

open() - 打打开文件并读取/写入文件内容。
readlines() - 读取文件的所有行并返回列表。
writelines() - 将字符串列表写入文件。
len() - 返回列表的长度。
需要注意的是，这个示例代码中，CONFIG_PATH变量指定了WireGuard的配置文件路径。在实际应用中，您需要根据自己的系统环境来修改这个变量的值。

另外，这个示例中，我们使用了基于文件的简单方式来存储WireGuard配置，实际应用中，您可能需要使用数据库或其他更高级的方式来存储和管理WireGuard配置。

总体来说，这个示例提供了一个简单但完整的后端应用程序示例，可以用来处理WireGuard配置的增删改查操作。您可以根据自己的需求来扩展这个示例，添加更多的逻辑和功能。
"""