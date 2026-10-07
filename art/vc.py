import json, subprocess, sys
import os
BIN=os.environ.get("VECTORCRAFT_CLI","vectorcraft-cli")
class VC:
    def __init__(s):
        s.p=subprocess.Popen([BIN,"mcp","--headless"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        s.i=0
        s.rpc("initialize",{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"s","version":"0"}})
        s.p.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"})+"\n"); s.p.stdin.flush()
    def rpc(s,m,params):
        s.i+=1; s.p.stdin.write(json.dumps({"jsonrpc":"2.0","id":s.i,"method":m,"params":params})+"\n"); s.p.stdin.flush()
        while True:
            d=json.loads(s.p.stdout.readline())
            if d.get("id")==s.i: return d
    def call(s,name,**a):
        d=s.rpc("tools/call",{"name":name,"arguments":a})
        if "error" in d: raise RuntimeError(d["error"])
        r=d["result"]
        txt="\n".join(c.get("text","") for c in r.get("content",[]) if c["type"]=="text")
        if r.get("isError"): raise RuntimeError(f"{name} {a}: {txt}")
        return txt
