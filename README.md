# 🧠 Resolução de Sudoku com IA e Interface Gráfica

Este projeto combina **técnicas de visão computacional** com uma interface em **Pygame** para resolver tabuleiros de Sudoku. O sistema permite **carregar imagens com tabuleiros reais**, extrair os números com redes neurais treinadas (em formato ONNX) e resolver o puzzle com **algoritmo de backtracking** clássico.

---

## 🚀 Funcionalidades

- 🖼️ Carregamento de tabuleiros a partir de imagens (.jpg, .png, .jpeg, .webp)
- 🔍 Processamento de imagem com OpenCV, Scipy e NumPy
- 🧠 Reconhecimento de dígitos com modelo ONNX treinado em MNIST
- 🧮 Resolução automática via backtracking
- 🎮 Interface interativa com Pygame

---

## 🧪 Tecnologias e Bibliotecas

| Biblioteca       | Finalidade                                      |
|------------------|--------------------------------------------------|
| `pygame`         | Interface gráfica, interação do usuário         |
| `opencv-python`  | Processamento e extração de células do tabuleiro|
| `numpy`          | Manipulação de matrizes                         |
| `scipy`          | Cálculo do centro de massa (alinhamento de dígitos) |
| `onnxruntime`    | Execução de modelos treinados no formato ONNX   |

---

## 🕹️ Controles

| Comando            |    Ação                                              |
|--------------------|------------------------------------------------------|
| Clique com o mouse |  Seleciona uma célula                                |
| Números (1–9)      | Insere número na célula selecionada                  |
| Backspace          | Apaga o número da célula selecionada                 |
| TAB                | Resolve automaticamente o tabuleiro via backtracking |
| Q                  | Carrega uma imagem com tabuleiro de Sudoku           |
| ESC                | Fecha o jogo                                         |

---

## 📷 Requisitos para carregar tabuleiros via imagem

Para que a leitura funcione corretamente:
- A imagem deve ser digital e conter o tabuleiro, de forma clara e legível
- A margem do tabuleiro deve estar destacada

---

## ⚙️ Como rodar

1. Instale as dependências:
```bash
pip install requirements.txt
```

2. Execute o projeto:
```bash
python main.py
```

> Obs: Certifique-se de que o arquivo `mnist-12.onnx` está no mesmo diretório do script principal.   

---

## 🧠 Modelo de Reconhecimento

- O script recebe uma imagem e tenta encontrar o tabuleiro
- O tabuleiro é separado em células
- As células são processados para facilitar o reconhecimento pelo modelo
- Células vazias já são separadas nesse processo
- O projeto utiliza um modelo `.onnx` treinado no dataset MNIST
- O modelo recebe imagens `28x28` e retorna a predição do dígito contido

---

## 🧩 Resolução do Sudoku

- Encontra-se um quadrado em branco
- Testam-se os números até que um seja válido na posição
- Encontra-se o próximo quadrado vazio
- Caso não haja número possível:
  - Volta ao quadrado anterior
  - Coloca o próximo número válido
- Repete

---

## 📦 Download do modelo ONNX

O modelo treinado usado para reconhecer os dígitos (`mnist-12.onnx`) pode ser baixado aqui:  
👉 [Download do modelo ONNX](https://github.com/onnx/models/tree/main/validated/vision/classification/mnist)

Após o download, coloque o arquivo na raiz do projeto.

---

## 📸 Exemplo de leitura de imagem e resolução automática

![explorer_idG8mcf9Nm](https://github.com/user-attachments/assets/92fa9a9a-e756-4355-a380-777bef6f2a7e)

---
