#!/bin/bash

# Nome do arquivo de saída
OUTPUT_FILE="all_git_files_concatenated.txt"

# Separador visual entre os arquivos
SEPARATOR="===================================================="

# Verifica se estamos em um repositório Git
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Erro: Este não é um diretório de trabalho Git."
    exit 1
fi

# Inicia o arquivo de saída (cria ou limpa)
> "$OUTPUT_FILE"

echo "Iniciando a concatenação dos arquivos rastreados pelo Git em: $OUTPUT_FILE"
echo "$SEPARATOR" >> "$OUTPUT_FILE"

# Usa 'git ls-files' para obter a lista de arquivos rastreados
# O argumento -z (null-termination) e o 'xargs -0' são usados para lidar corretamente
# com nomes de arquivos que contenham espaços ou outros caracteres especiais.
git ls-files -z | while IFS= read -r -d $'\0' FILE_PATH; do
    # Verifica se o arquivo existe e é regular (para evitar links simbólicos ou diretórios, embora o git ls-files já ajude)
    if [ -f "$FILE_PATH" ]; then
        echo "Adicionando: $FILE_PATH"
        
        # Escreve o caminho completo do arquivo no arquivo de saída
        echo "--- ARQUIVO: $(pwd)/$FILE_PATH ---" >> "$OUTPUT_FILE"
        
        # Concatena o conteúdo do arquivo
        cat "$FILE_PATH" >> "$OUTPUT_FILE"
        
        # Adiciona o separador
        echo -e "\n$SEPARATOR\n" >> "$OUTPUT_FILE"
    else
        echo "Aviso: Ignorando caminho não-arquivo ou inexistente: $FILE_PATH"
    fi
done

echo "Concluído! Todos os arquivos rastreados foram concatenados em $OUTPUT_FILE."
