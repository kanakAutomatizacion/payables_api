from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from reglas import REGLAS_CUENTA_CONTABLE, CUENTA_POR_DEFECTO

app = FastAPI()

@app.post("/completar-cuenta")
async def completar_cuenta(request: Request):
    data = await request.json()
    
    nit_vendedor = data.get("factura", {}).get("Nit_Vendedor", "")
    cuenta_asignada = REGLAS_CUENTA_CONTABLE.get(nit_vendedor, CUENTA_POR_DEFECTO)

    for item in data.get("items", []):
        item["cuentacontable"] = cuenta_asignada

    return JSONResponse(content=data)
