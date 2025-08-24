#!/usr/bin/env python3

import json
from proxmoxer import ProxmoxAPI
import os
import math

min_ram = 2
min_cpu = 1

api_url = os.environ.get("TF_VAR_proxmox_api_url")
api_user = os.environ.get("TF_VAR_proxmox_api_token_id")
api_token = os.environ.get("TF_VAR_proxmox_api_secret_token")
token_name = os.environ.get("proxmox_token_name")
user_name = api_user.split("!")[0]

print(token_name, user_name)

proxmox = ProxmoxAPI(
    api_url.replace("https://", "").replace("http://", ""),
    user=user_name,
    token_name=token_name,
    token_value=api_token,
    verify_ssl=False
)

nodes = proxmox.nodes.get()

best_node = None
max_score = -1


for node in nodes:
    total_cores = node["maxcpu"]
    used_cores = node["cpu"] * total_cores
    free_cores = math.floor(total_cores - used_cores)

    print(node["node"])
    print(free_cores, used_cores)

    free_mem = (node["maxmem"] - node["mem"]) / 2**30
    print(free_mem)

    score = free_cores * 10 + free_mem

    if free_cores < min_cpu or free_mem < min_ram:
        continue

    if score > max_score:
        max_score = score
        best_node = node["node"]

if not best_node:
    raise Exception("In current config no node is viable to start a VM")

print(json.dumps({"best_node": best_node}))
