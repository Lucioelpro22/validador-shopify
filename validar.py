"""Convierte un catálogo simple de productos sin variantes a CSV."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

def convertir(origen, destino):
    productos = []
    usados = set()
    errores = []
    with origen.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if not {"handle", "titulo", "precio"} <= set(lector.fieldnames or []):
            raise ValueError("Se requieren las columnas handle,titulo,precio")
        if len(set(lector.fieldnames)) != len(lector.fieldnames):
            raise ValueError("El encabezado contiene nombres de columna repetidos")
        for fila in lector:
            handle, titulo, precio = ((fila[k] or "").strip() for k in ("handle", "titulo", "precio"))
            try:
                importe = Decimal(precio)
            except InvalidOperation:
                importe = Decimal("NaN")
            motivos = []
            if not handle:
                motivos.append("falta el handle")
            elif handle.casefold() in usados:
                motivos.append("handle repetido")
            if not titulo:
                motivos.append("falta el título")
            if not importe.is_finite() or importe < 0 or importe.adjusted() > 15:
                motivos.append("precio inválido o fuera de rango")
            if None in fila:
                motivos.append("sobran columnas")
            if motivos:
                errores.append(f"Fila {lector.line_num}: {', '.join(motivos)}")
                continue
            usados.add(handle.casefold())
            productos.append((handle, titulo, format(importe, "f")))
    if errores:
        raise ValueError("\n".join(errores))
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
