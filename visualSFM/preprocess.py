import csv

def trocar_pontos_por_virgulas(arquivo_entrada, arquivo_saida=None):
    """
    Lê um arquivo CSV e troca pontos por vírgulas.
    
    Args:
        arquivo_entrada (str): Caminho do arquivo CSV de entrada
        arquivo_saida (str): Caminho do arquivo CSV de saída. 
        Se None, sobrescreve o arquivo de entrada
    """
    
    if arquivo_saida is None:
        arquivo_saida = arquivo_entrada
    
    try:
        # Lê o arquivo e substitui pontos por vírgulas
        with open(arquivo_entrada, 'r', encoding='utf-8') as entrada:
            conteudo = entrada.read()
        
        # Substitui todos os pontos por vírgulas
        conteudo_modificado = conteudo.replace('.', ',')
        
        # Escreve no arquivo de saída
        with open(arquivo_saida, 'w', encoding='utf-8') as saida:
            saida.write(conteudo_modificado)
        
        print(f"✓ Arquivo processado com sucesso!")
        print(f"  Entrada: {arquivo_entrada}")
        print(f"  Saída: {arquivo_saida}")
        
    except Exception as e:
        print(f"✗ Erro ao processar arquivo: {e}")


if __name__ == "__main__":
    # Processa o arquivo adriana2.csv
    trocar_pontos_por_virgulas("adriana2.csv")
