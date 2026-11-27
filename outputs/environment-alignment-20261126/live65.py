import urllib.request
print(urllib.request.urlopen('http://127.0.0.1:18082/server_info?config_format=json',timeout=10).read().decode())
