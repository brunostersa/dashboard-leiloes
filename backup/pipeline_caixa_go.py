import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import time
import os

# 1. BAIXAR CSV ATUALIZADO DO SITE DA CAIXA
def baixar_csv_goias():
    url = "https://venda-imoveis.caixa.gov.br/sistema/lista.asp"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://venda-imoveis.caixa.gov.br/sistema/download-lista.asp"
    }

    # O campo 'selUf' é o valor do select
    data = {
        "selUf": "GO",  # Estado de Goiás
        "cbxTipoImovel": "0",
        "cbxFormaVenda": "0",
        "cbxFaixaValor": "0",
        "cbxSituacaoOcupacao": "0",
        "hdnPagina": "1",
        "hdnOrdem": "1",
        "hdnSentido": "asc"
    }

    # Primeiro fazemos a requisição para gerar a lista de imóveis
    sessao = requests.Session()
    sessao.post(url, headers=headers, data=data)

    # Em seguida, baixamos o CSV
    download_url = "https://venda-imoveis.caixa.gov.br/sistema/arquivo/GO.csv"
    resposta = sessao.get(download_url, headers=headers)

    if resposta.status_code == 200:
        df = pd.read_csv(BytesIO(resposta.content), sep=";", encoding="latin1", skiprows=5)
        df.to_csv("go.csv", index=False, sep=";", encoding="utf-8")
        print("✅ CSV de Goiás salvo como go.csv")
        return df
    else:
        raise Exception("❌ Erro ao baixar o arquivo CSV gerado.")


# 2. FAZER SCRAPING DOS LINKS
def extrair_detalhes(link):
    try:
        resp = requests.get(link, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        def pegar(b):
            tag = soup.find("b", string=b)
            return tag.next_sibling.strip(" :\n\r\t") if tag and tag.next_sibling else ""

        return {
            "Link": link,
            "Título": soup.find("span", {"id": "lblTituloImovel"}).text.strip() if soup.find("span", {"id": "lblTituloImovel"}) else "",
            "Descrição": soup.find("span", {"id": "lblDescricaoImovel"}).text.strip() if soup.find("span", {"id": "lblDescricaoImovel"}) else "",
            "FormasPagamento": pegar("Forma de Pagamento"),
            "TempoRestante": pegar("Data do encerramento"),
            "Valor avaliação": pegar("Valor de Avaliação"),
            "Valor venda": pegar("Valor de Venda"),
            "Permite FGTS": "Sim" if "FGTS" in pegar("Forma de Pagamento").upper() else "Não",
            "Permite financiamento": "Sim" if "SFI" in pegar("Forma de Pagamento").upper() else "Não"
        }
    except Exception as e:
        return {
            "Link": link,
            "Título": "",
            "Descrição": "",
            "FormasPagamento": "",
            "TempoRestante": "",
            "Valor avaliação": "",
            "Valor venda": "",
            "Permite FGTS": "Não",
            "Permite financiamento": "Não"
        }

# 3. EXECUTA O PROCESSO DE SCRAPING
def processar_links(df, limite=50):
    print(f"🔎 Coletando dados detalhados de {limite} imóveis...")
    links = df["Link"].dropna().unique().tolist()
    resultados = []

    for i, link in enumerate(links[:limite]):
        print(f"➡️ {i+1}/{limite} - {link}")
        resultados.append(extrair_detalhes(link))
        time.sleep(1.5)

    return pd.DataFrame(resultados)

# 4. CALCULAR DESCONTO
def calcular_desconto(row):
    try:
        valor_av = float(row["Valor avaliação"].replace(".", "").replace(",", "."))
        valor_venda = float(row["Valor venda"].replace(".", "").replace(",", "."))
        return round(100 * (1 - valor_venda / valor_av), 2)
    except:
        return None

# 5. RODAR TUDO
def rodar_pipeline():
    df_base = baixar_csv_goias()
    df_detalhado = processar_links(df_base, limite=50)
    df_detalhado["Desconto (%)"] = df_detalhado.apply(calcular_desconto, axis=1)

    df_detalhado.to_csv("imoveis_goias_estrategico.csv", index=False, sep=";", encoding="utf-8")
    print("✅ Arquivo salvo: imoveis_goias_estrategico.csv")

if __name__ == "__main__":
    rodar_pipeline()
