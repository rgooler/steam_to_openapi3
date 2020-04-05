import requests
import json

oapi = json.loads("""
{
  "openapi": "3.0.0",
  "info": {
      "title": "Steam Web API",
      "termsOfService": "https://steamcommunity.com/dev/apiterms",
      "contact": {
        "name": "Valve Software",
        "url": "https://help.steampowered.com/"
      },
      "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://api.steampowered.com"
    }
  ],
  "paths": {},
  "components": {}
}""")

url = "https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001"

r = requests.get(url)
j = r.json()

# Transform steam output to openapi v3
for interface in j['apilist']['interfaces']:
    i_name = interface['name']
    for method in interface['methods']:
        m_name = method['name']
        version = "v" + str(method['version']).zfill(4)
        path = f"/{i_name}/{m_name}/{version}"
        m = method['httpmethod'].lower()
        if path not in oapi['paths']:
            oapi['paths'][path] = {}
        oapi['paths'][path][m] = {}
        p = oapi['paths'][path][m]
        p['parameters'] = []
        for param in method['parameters']:
            pp = {}
            pp['name'] = param['name']
            pp['in'] = 'query'
            if 'description' in param.keys():
                pp['description'] = param['description']
            pp['schema'] = {}
            if param['type'] in ['uint32', 'uint64', 'int32', 'int64']:
                pp['schema']['type'] = 'integer'
                pp['schema']['format'] = param['type']
            elif param['type'] in ['{message}']:
                pp['schema']['type'] = 'string'
                pp['schema']['format'] = param['type']
            elif param['type'] in ['rawbinary']:
                pp['schema']['type'] = 'string'
                pp['schema']['format'] = 'binary'
            else:
                pp['schema']['type'] = param['type']
            pp['required'] = not param['optional']
            
            p['parameters'].append(pp)
            
# save json file
with open('openapi.json', 'w', encoding='utf-8') as f:
    json.dump(oapi, f, indent=4, ensure_ascii=False, sort_keys=True)
