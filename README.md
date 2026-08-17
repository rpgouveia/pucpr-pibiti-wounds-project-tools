# pucpr-pibiti-wounds-project-tools

Ferramentas em Python para preparar imagens térmicas e arquivos auxiliares usados no fluxo de trabalho com Meshroom / VisualSFM.

## O que esta ferramenta faz

O `main.py` pega as imagens térmicas de entrada, associa cada uma a uma vista do `cameraInit.sfm`, redimensiona para a resolução esperada, renomeia o arquivo pelo `viewId` e gera um CSV com o mapeamento final.

Também há scripts auxiliares em `visualSFM/` para pequenas tarefas de manutenção de arquivos e CSV.

## Requisitos

- Python 3
- Pillow
- python-dotenv

Instalação das dependências:

```bash
py -m pip install -r requirements.txt
```

## Configuração

O script principal lê as configurações de um arquivo `.env`. O modelo de referência está em `.env.example`.

Campos esperados:

- `SFM_PATH`: caminho do `cameraInit.sfm`
- `IR_PATH`: pasta com as imagens térmicas de entrada
- `OUT_PATH`: pasta de saída com nomes baseados em `viewId`
- `RESIZED_PATH`: pasta opcional para salvar cópias redimensionadas com nome original
- `CSV_PATH`: caminho opcional do CSV de mapeamento
- `EXTENSAO_SAIDA`: `.png` ou `.jpg`
- `FORCAR_SOBRESCRITA`: `true` ou `false`

Exemplo:

```env
SFM_PATH=C:\MeshroomCache\CameraInit\hash_do_no\cameraInit.sfm
IR_PATH=C:\Imagens\IR
OUT_PATH=C:\Saida\IR-viewid
RESIZED_PATH=C:\Saida\IR-resized
CSV_PATH=C:\Saida\mapa_viewid.csv
EXTENSAO_SAIDA=.png
FORCAR_SOBRESCRITA=false
```

## Como usar

Execução padrão:

```bash
py main.py
```

Sobrescrevendo o arquivo `.env` por linha de comando:

```bash
py main.py --env "D:\coletas\semana12\config.env"
py main.py --sfm "C:\caminho\cameraInit.sfm"
py main.py --ir "C:\caminho\imagens_termicas"
py main.py --out "C:\caminho\saida"
py main.py --nao-forcar
```

## Resultado gerado

Ao final da execução, o script cria:

- imagens térmicas renomeadas por `viewId`
- cópias redimensionadas, se `RESIZED_PATH` estiver definido
- um CSV com status, nomes de arquivo e dimensões antes/depois

O pareamento entre a imagem visível e a térmica é feito pelo nome base do arquivo, ignorando a extensão.

## Scripts auxiliares

- `visualSFM/preprocess.py`: troca pontos por vírgulas em um arquivo CSV.
- `visualSFM/remover_mat_sift.py`: remove arquivos `*.mat` e `*.sift` de uma pasta.

## Observações

- O script principal aceita extensões de entrada como `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tif` e `.tiff`.
- Se uma imagem térmica não existir para uma vista do SfM, ela será marcada como ausente no CSV.
- O texto do CSV usa separador `;` e codificação UTF-8 com BOM para facilitar a abertura no Excel.