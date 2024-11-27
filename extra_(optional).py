import os

def renomear_arquivos_com_underscore(diretorio):
    """
    Renomeia todos os arquivos .md que contêm '_' no nome:
    - Substitui '_' por espaços.
    - Adiciona '(merged)' ao final do nome antes da extensão.
    """
    # Lista todos os arquivos no diretório
    arquivos = os.listdir(diretorio)
    arquivos_md = [f for f in arquivos if f.lower().endswith('.md')]

    if not arquivos_md:
        print("Nenhum arquivo .md encontrado na pasta especificada.")
        return

    print(f"Foram encontrados {len(arquivos_md)} arquivos .md na pasta.")

    for arquivo in arquivos_md:
        if '_' in arquivo:
            # Divide o nome e a extensão
            nome, ext = os.path.splitext(arquivo)
            # Substitui '_' por espaços
            novo_nome = nome.replace('_', ' ')
            # Adiciona '(merged)' ao final
            novo_nome += " (merged)"
            # Recombina com a extensão
            novo_nome += ext

            caminho_antigo = os.path.join(diretorio, arquivo)
            caminho_novo = os.path.join(diretorio, novo_nome)

            # Verifica se o novo nome já existe
            if os.path.exists(caminho_novo):
                print(f"Aviso: O arquivo '{novo_nome}' já existe. Renomeamento de '{arquivo}' foi ignorado para evitar sobrescrição.")
                continue

            try:
                os.rename(caminho_antigo, caminho_novo)
                print(f"Renomeado: '{arquivo}' -> '{novo_nome}'")
            except Exception as e:
                print(f"Erro ao renomear '{arquivo}': {e}")
        else:
            print(f"Não há necessidade de renomear: '{arquivo}'")

def main():
    print("=== Script de Renomeação de Arquivos .md ===")
    diretorio = input("Digite o caminho da pasta onde estão os arquivos .md: ").strip()

    if not os.path.isdir(diretorio):
        print("Diretório inválido. Verifique o caminho e tente novamente.")
        return

    renomear_arquivos_com_underscore(diretorio)
    print("Processo concluído.")

if __name__ == "__main__":
    main()
