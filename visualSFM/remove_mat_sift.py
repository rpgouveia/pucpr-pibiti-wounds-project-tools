import os
import glob

def remover_arquivos_especificos(caminho_diretorio):
    # Define os padrões de arquivo a serem removidos
    padroes = ['*.mat', '*.sift']
    
    for padrao in padroes:
        # Busca todos os arquivos que correspondem ao padrão no diretório
        arquivos = glob.glob(os.path.join(caminho_diretorio, padrao))
        
        for arquivo in arquivos:
            try:
                os.remove(arquivo)
                print(f"Removido: {arquivo}")
            except OSError as e:
                print(f"Erro ao remover {arquivo}: {e}")

# Exemplo de uso:
# substitua '/caminho/para/sua/pasta' pelo caminho real
caminho = r'C:\Users\Renato\Documents\PUCPR\PIBIT-ProjectWounds\pacientes\danielle\sel_danielle_fr_rainHi'
remover_arquivos_especificos(caminho)