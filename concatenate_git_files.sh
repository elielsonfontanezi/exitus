#!/bin/bash

# Nome do arquivo de saída
OUTPUT_FILE="all_git_text_files_concatenated.txt"

# Separador visual entre os arquivos
SEPARATOR="===================================================="

# Verifica se estamos em um repositório Git
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Erro: Este não é um diretório de trabalho Git."
    exit 1
fi

# Inicia o arquivo de saída (cria ou limpa)
> "$OUTPUT_FILE"

echo "Iniciando a concatenação **apenas de arquivos de texto** rastreados pelo Git em: $OUTPUT_FILE"
echo "$SEPARATOR" >> "$OUTPUT_FILE"

# Usa 'git ls-files' para obter a lista de arquivos rastreados
# O argumento -z (null-termination) e o 'xargs -0' são usados para lidar corretamente
# com nomes de arquivos que contenham espaços ou outros caracteres especiais.
git ls-files -z | while IFS= read -r -d $'\0' FILE_PATH; do
    # Verifica se o arquivo existe e é regular
    if [ -f "$FILE_PATH" ]; then
        
        # O principal ajuste: Verifica se o arquivo é do tipo texto usando 'file --mime-type -b'
        # -b: Não imprime o nome do arquivo, apenas o tipo MIME
        # O tipo MIME de arquivos de texto geralmente começa com 'text/' (ex: text/plain, text/x-shellscript, text/html)
        MIME_TYPE=$(file --mime-type -b "$FILE_PATH")
        
        if [[ "$MIME_TYPE" == text/* ]]; then
            echo "Adicionando (Tipo: $MIME_TYPE): $FILE_PATH"

            # Escreve o caminho completo do arquivo no arquivo de saída
            echo "--- ARQUIVO: $(pwd)/$FILE_PATH ---" >> "$OUTPUT_FILE"

            # Concatena o conteúdo do arquivo
            cat "$FILE_PATH" >> "$OUTPUT_FILE"

            # Adiciona o separador
            echo -e "\n$SEPARATOR\n" >> "$OUTPUT_FILE"
        else
            echo "Ignorando arquivo não-texto (Tipo: $MIME_TYPE): $FILE_PATH"
        fi
    else
        echo "Aviso: Ignorando caminho não-arquivo ou inexistente: $FILE_PATH"
    fi
done

echo "Concluído! Apenas arquivos de texto rastreados foram concatenados em $OUTPUT_FILE."
