# News Transfer Py
![Python](https://img.shields.io/badge/python-v3.8%2B-blue)
![GitHub last commit](https://img.shields.io/github/last-commit/AzeemIdrisi/PhoneSploit-Pro?logo=github)

Software utilizado para transferência de arquivos para um servidor de vídeo. 

## :rocket: Começando
Ao fazer o clone do projeto será necessário criar e habilitar a virtual env

### Criar venv
python -m venv venv

### Habilitar venv via prompt (caso não utilize o editor PyCharm)
. .\venv\Script\acrivate

### Habilitar venv no editor PyCharm
Como estou usando o PyCharm eu apenas apontei o interpretador para o python da venv criada e não precisei ativar 
via comando.

##Pré-requisitos

### Pacotes importados 
* ttkbootstrap - Bootstrap para tkinter
* Pillow - Manipulação de imagens, aqui utiizado para os ícones
* peewee - ORM
* pyinstaller - Gera o executável

## Executando os testes

### Executando todos os testes do Unittest
python -m unittest -v

## Gerando o executável

### Gerando o executável com pyinstaller
pyinstaller --noconsole --name="NewsTransferPy" --add-data="src\app\assets;.\src\app\assets" --icon=src\app\assets\favicon.ico --collect-all "ttkbootstrap" --collect-all "peewee" main.py

#### Parâmetros
--noconsole: não exibe a janela de console

--name: nome da aplicação

--add-data: copia a pasta de assets

--icon: icone da aplicação

--collect-all: copia tudo sobre o módulo especificado

## Observações
### Observação quanto ao desenvolvimento
Copiar o arquivo ffmpeg.exe para a pasta raiz do programa. Por causa do tamanho do arquivo não possível subir para o 
github.

### Observação quanto a geração do executável
Depois de gerado o executável é necessário copiar o ffmpeg.exe para dentro da pasta NewsTransferPy que contém o executável NewsTransferPy.exe.

### Versão do ffmpeg utilizado
ffmpeg version N-109430-g7af947c0c0-20221218 Copyright (c) 2000-2022 --extra-version=20221218

A não utilização desta versão poderá impactar no método get_duration() da classe src\business\utils\ConvertVideo