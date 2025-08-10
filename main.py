from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from reglas import REGLAS_CUENTA_CONTABLE, CUENTA_POR_DEFECTO

app = FastAPI()

@app.post("/completar-cuenta")
async def completar_cuenta(request: Request):
    raw_data = await request.json()
    
    # Si viene con el formato de Automate, extraemos el body real
    data = raw_data.get("body", raw_data)
    
    nit_vendedor = data.get("factura", {}).get("Nit_Vendedor", "")
    cuenta_asignada = REGLAS_CUENTA_CONTABLE.get(nit_vendedor, CUENTA_POR_DEFECTO)

    for item in data.get("items", []):
        item["cuentacontable"] = cuenta_asignada

    return JSONResponse(content=data)