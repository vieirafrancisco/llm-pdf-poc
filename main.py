import csv

import PyPDF2
import google.generativeai as genai
from nltk.tokenize import word_tokenize
from environs import Env

env = Env()
env.read_env()

# https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = env.str('GOOGLE_API_KEY', '')


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text


def process_text_with_gemini(text):
    # Tokenização
    tokens = word_tokenize(text)

    # Junta os tokens novamente em uma string para passar para o Gemini
    # (Você pode personalizar essa junção para suas necessidades)
    processed_text = " ".join(tokens)

    # Configura a sua chave API do Gemini
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.0-pro-latest')

    # Exemplo: Resumir o texto
    prompt = (
        f'No texto "{processed_text}", retorne no formato csv '
        'todas as transações seguindo a regra: '
        'data, descrição, valor, parcela atual, total parcelas. '
        'O valor precisa ser somente digitos '
        'com o divisor decimal ".". '
        'Quando na descrição tiver o padrão x/y, em que x e y são digitos,'
        'separe os digitos x e y da "/" e '
        'posicione o digito x na coluna "parcela atual" '
        'e o digito y na coluna "total parcelas". '
        'Caso não tenha esse padrão posicione ambas com valor 1.'
    )
    response = model.generate_content(prompt)
    return response


def format_and_save_to_csv(summary):
    with open('log.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow((
            'date', 'description', 'value', 'installment', 'total installments'
        ))
        writer.writerows((
            line.split(',') for line in summary.text.split('\n')
        ))


# Substitua 'seu_arquivo.pdf' pelo caminho do seu arquivo
pdf_path = 'seu_arquivo.pdf'
text = extract_text_from_pdf(pdf_path)
summary = process_text_with_gemini(text)
