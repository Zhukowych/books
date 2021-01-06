import os
import json

os.system('./node_modules/.bin/webpack')
with open("webpack-stats.json", "r") as file:
    data = json.loads(file.read())

data['chunks']['main'][0]['publicPath'] = 'http://127.0.0.1:8000/static/app.js'
data_str = json.dumps(data)
with open("webpack-stats.json", "w") as file:
    file.write(data_str)

