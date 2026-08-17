#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
-------------------
Prepara as imagens térmicas para uso como segunda camada de textura no Meshroom.

Executa, em uma única passagem:
  1) redimensionamento por vizinho mais próximo (NEAREST) de 640x480 para a
     resolução registrada em cada vista do cameraInit.sfm (768x576);
    2) cópia renomeada pelo viewId correspondente, exigida pelo atributo
     "Images Folder" do nó Texturing2;
  3) registro do vínculo em arquivo CSV para conferência e reuso.

O pareamento entre imagem visível e imagem térmica é feito pelo nome do arquivo
sem extensão (HM_12151.jpeg  <->  HM_12151.jpg), de modo que a diferença de
extensão entre os dois canais não interfere.

CONFIGURAÇÃO
    Os caminhos ficam no arquivo .env. Com ele preenchido, a execução é apenas:

        py main.py

    Argumentos de linha de comando têm precedência sobre o .env:

        py main.py --env "D:\\coletas\\semana12\\config.env"
        py main.py --sfm "C:\\...\\<novo-hash>\\cameraInit.sfm"
        py main.py --nao-forcar

Requisitos:  py -m pip install pillow python-dotenv
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("ERRO: Pillow nao encontrado. Instale com:  py -m pip install pillow")

try:
    from dotenv import load_dotenv, find_dotenv
except ImportError:
    sys.exit("ERRO: python-dotenv nao encontrado. Instale com:  py -m pip install python-dotenv")

# Extensões aceitas na pasta de imagens térmicas de origem.
EXTENSOES_ENTRADA = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

VERDADEIROS = ("true", "1", "yes", "sim")


def carregar_vistas(caminho_sfm):
    """Lê o cameraInit.sfm e devolve a lista de vistas com viewId, nome e dimensões."""
    with open(caminho_sfm, "r", encoding="utf-8") as f:
        dados = json.load(f)

    vistas = []
    for v in dados.get("views", []):
        # O campo "path" usa barras normais mesmo no Windows.
        caminho = v["path"].replace("\\", "/")
        nome = caminho.rsplit("/", 1)[-1]
        radical = nome.rsplit(".", 1)[0]
        vistas.append({
            "viewId": v["viewId"],
            "frameId": v.get("frameId", ""),
            "arquivo_visivel": nome,
            "radical": radical,
            "largura": int(v["width"]),
            "altura": int(v["height"]),
        })
    return vistas


def indexar_termicas(pasta_ir):
    """Mapeia radical (minúsculo) -> caminho do arquivo térmico."""
    indice = {}
    duplicados = []
    for arq in sorted(Path(pasta_ir).iterdir()):
        if not arq.is_file() or arq.suffix.lower() not in EXTENSOES_ENTRADA:
            continue
        chave = arq.stem.lower()
        if chave in indice:
            duplicados.append(arq.name)
            continue
        indice[chave] = arq
    return indice, duplicados


def resolver_configuracao():
    """Combina .env e linha de comando. A linha de comando tem precedência."""
    ap = argparse.ArgumentParser(
        description="Redimensiona (vizinho mais próximo) e renomeia imagens térmicas "
                "por viewId. Os caminhos vêm do .env; os argumentos abaixo o sobrepõem."
    )
    ap.add_argument("--env", help="caminho de um .env alternativo")
    ap.add_argument("--sfm", help="caminho do cameraInit.sfm")
    ap.add_argument("--ir", help="pasta com as imagens térmicas originais")
    ap.add_argument("--out", help="pasta de saída, nomeada por viewId")
    ap.add_argument("--resized", help="pasta das redimensionadas com nome original")
    ap.add_argument("--csv", help="caminho do CSV de mapeamento")
    ap.add_argument("--ext", help="formato de saída: .png ou .jpg")
    g = ap.add_mutually_exclusive_group()
    g.add_argument(
        "--forcar", dest="forcar", action="store_true",
        help="sobrescreve arquivos já existentes na saída"
    )
    g.add_argument(
        "--nao-forcar", dest="forcar", action="store_false",
        help="preserva arquivos já existentes, ignorando o .env"
    )
    ap.set_defaults(forcar=None)
    args = ap.parse_args()

    # .env explícito tem prioridade; senão busca a partir da pasta atual e sobe.
    if args.env:
        caminho_env = Path(args.env)
        if not caminho_env.is_file():
            sys.exit(f"ERRO: .env não encontrado: {caminho_env}")
    else:
        encontrado = find_dotenv(usecwd=True)
        caminho_env = Path(encontrado) if encontrado else None

    if caminho_env:
        load_dotenv(caminho_env, override=True)

    def cfg(valor_cli, chave, padrao=None):
        valor = valor_cli or os.getenv(chave) or padrao
        return valor.strip() if isinstance(valor, str) else valor

    # Normalização e validação manuais: o argparse não aplica "choices" a
    # valores vindos de default, de modo que um "png" no .env passaria intacto
    # e geraria arquivos sem extensão.
    ext = cfg(args.ext, "EXTENSAO_SAIDA", ".png").lower()
    if not ext.startswith("."):
        ext = "." + ext
    if ext == ".jpeg":
        ext = ".jpg"
    if ext not in (".png", ".jpg"):
        sys.exit(f"ERRO: EXTENSAO_SAIDA deve ser .png ou .jpg (recebido: {ext})")

    forcar = (
        args.forcar if args.forcar is not None
        else os.getenv("FORCAR_SOBRESCRITA", "false").strip().lower() in VERDADEIROS
    )

    cfg_final = {
        "env": caminho_env,
        "sfm": cfg(args.sfm, "SFM_PATH"),
        "ir": cfg(args.ir, "IR_PATH"),
        "out": cfg(args.out, "OUT_PATH"),
        "resized": cfg(args.resized, "RESIZED_PATH"),
        "csv": cfg(args.csv, "CSV_PATH"),
        "ext": ext,
        "forcar": forcar,
    }

    rotulos = {"sfm": "SFM_PATH / --sfm", "ir": "IR_PATH / --ir", "out": "OUT_PATH / --out"}
    faltando = [rotulos[k] for k in ("sfm", "ir", "out") if not cfg_final[k]]
    if faltando:
        print("ERRO: parâmetros obrigatórios não informados: " + ", ".join(faltando))
        if not caminho_env:
            print("Nenhum .env foi encontrado. Copie o .env.example para .env e edite os caminhos.")
        sys.exit(1)

    return cfg_final


def main():
    cfg = resolver_configuracao()

    caminho_sfm = Path(cfg["sfm"])
    pasta_ir = Path(cfg["ir"])
    pasta_out = Path(cfg["out"])
    pasta_resized = Path(cfg["resized"]) if cfg["resized"] else None
    caminho_csv = Path(cfg["csv"]) if cfg["csv"] else pasta_out / "mapa_viewid.csv"
    ext = cfg["ext"]

    print(f"Configuração ............. {cfg['env'] or 'somente linha de comando'}")
    print(f"SfM ...................... {caminho_sfm}")
    print(f"Térmicas ................. {pasta_ir}")
    print(f"Saída (viewId) ........... {pasta_out}")
    print(f"Formato / sobrescrever ... {ext} / {'sim' if cfg['forcar'] else 'não'}")

    for p, rotulo in ((caminho_sfm, "cameraInit.sfm"), (pasta_ir, "pasta de imagens térmicas")):
        if not p.exists():
            sys.exit(f"ERRO: {rotulo} não encontrado: {p}")

    pasta_out.mkdir(parents=True, exist_ok=True)
    if pasta_resized:
        pasta_resized.mkdir(parents=True, exist_ok=True)

    vistas = carregar_vistas(caminho_sfm)
    indice, duplicados = indexar_termicas(pasta_ir)

    print("-" * 56)
    print(f"Vistas no SfM ............ {len(vistas)}")
    print(f"Térmicas encontradas ..... {len(indice)}")
    if duplicados:
        print(f"AVISO: radicais duplicados na pasta térmica, ignorados: {', '.join(duplicados)}")

    linhas = []
    processadas = 0
    ausentes = []
    usados = set()

    for v in vistas:
        chave = v["radical"].lower()
        origem = indice.get(chave)

        if origem is None:
            ausentes.append(v["arquivo_visivel"])
            linhas.append({
                "viewId": v["viewId"], "frameId": v["frameId"],
                "arquivo_visivel": v["arquivo_visivel"], "arquivo_termico": "",
                "arquivo_saida": "", "largura_original": "", "altura_original": "",
                "largura_final": v["largura"], "altura_final": v["altura"],
                "status": "AUSENTE",
            })
            continue

        usados.add(chave)
        destino = pasta_out / f"{v['viewId']}{ext}"

        if destino.exists() and not cfg["forcar"]:
            status = "JA_EXISTIA"
            with Image.open(origem) as img:
                lo, ao = img.size
        else:
            with Image.open(origem) as img:
                lo, ao = img.size
                img = img.convert("RGB")
                if (lo, ao) == (v["largura"], v["altura"]):
                    redim = img.copy()
                    status = "OK_SEM_REDIMENSIONAR"
                else:
                    redim = img.resize((v["largura"], v["altura"]), resample=Image.NEAREST)
                    status = "OK"

                if ext == ".png":
                    redim.save(destino, format="PNG", optimize=True)
                else:
                    redim.save(destino, format="JPEG", quality=100, subsampling=0)

                if pasta_resized:
                    copia = pasta_resized / f"{origem.stem}{ext}"
                    if ext == ".png":
                        redim.save(copia, format="PNG", optimize=True)
                    else:
                        redim.save(copia, format="JPEG", quality=100, subsampling=0)

        processadas += 1
        linhas.append({
            "viewId": v["viewId"], "frameId": v["frameId"],
            "arquivo_visivel": v["arquivo_visivel"], "arquivo_termico": origem.name,
            "arquivo_saida": destino.name, "largura_original": lo, "altura_original": ao,
            "largura_final": v["largura"], "altura_final": v["altura"],
            "status": status,
        })

    sobrando = sorted(set(indice) - usados)

    campos = [
        "viewId", "frameId", "arquivo_visivel", "arquivo_termico", "arquivo_saida",
        "largura_original", "altura_original", "largura_final", "altura_final", "status"
    ]
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        w.writeheader()
        w.writerows(linhas)

    print("-" * 56)
    print(f"Processadas .............. {processadas}/{len(vistas)}")
    print(f"Sem par térmico .......... {len(ausentes)}")
    if ausentes:
        print("   " + ", ".join(ausentes[:10]) + (" ..." if len(ausentes) > 10 else ""))
    print(f"Térmicas sem vista no SfM  {len(sobrando)}")
    if sobrando:
        print("   " + ", ".join(sobrando[:10]) + (" ..." if len(sobrando) > 10 else ""))
    print(f"CSV ...................... {caminho_csv}")

    if ausentes:
        print("\nATENÇÃO: há vistas sem imagem térmica correspondente. O nó Texturing")
        print("descartará essas câmeras na projeção da textura térmica.")


if __name__ == "__main__":
    main()