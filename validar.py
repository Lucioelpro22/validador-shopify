"""Convierte un catálogo simple de productos sin variantes a CSV."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

def convertir(origen, destino):
    productos = []
    usados = set()
    with origen.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if not {"handle", "titulo", "precio"} <= set(lector.fieldnames or []):
            raise ValueError("Se requieren las columnas handle,titulo,precio")
        for fila in lector:
            handle, titulo, precio = ((fila[k] or "").strip() for k in ("handle", "titulo", "precio"))
            try:
                importe = Decimal(precio)
            except InvalidOperation:
                importe = Decimal("NaN")
            if (not handle or not titulo or handle.casefold() in usados or
                    not importe.is_finite() or importe < 0 or None in fila):
                raise ValueError(f"Fila {lector.line_num}: revisá handle duplicado, título, precio o columnas")
            usados.add(handle.casefold())
            productos.append((handle, titulo, format(importe, "f")))
    if not productos:
        raise ValueError("El catálogo está vacío")
    with destino.open("x", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(("Handle", "Title", "Variant Price"))
        escritor.writerows(productos)
    return len(productos)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origen", type=Path)
    parser.add_argument("destino", type=Path)
    args = parser.parse_args()
    try:
        print(f"{convertir(args.origen, args.destino)} productos preparados")
    except (ValueError, OSError, csv.Error) as error:
        parser.exit(1, f"{error}\n")
