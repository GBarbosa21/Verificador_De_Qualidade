import streamlit as st
import fitz  # PyMuPDF
import io

# --- FUNÇÃO PRINCIPAL PARA ANÁLISE DO PDF ---
def extrair_dpi_de_pdf(conteudo_pdf_em_bytes):
    # ... (O conteúdo desta função permanece o mesmo) ...
    resultados = []
    try:
        documento = fitz.open("pdf", conteudo_pdf_em_bytes)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo PDF: {e}")
        return []
    for num_pagina in range(len(documento)):
        pagina = documento.load_page(num_pagina)
        lista_de_imagens = pagina.get_images(full=True)
        if not lista_de_imagens:
            continue
        for img_info in lista_de_imagens:
            xref = img_info[0]
            base_image = documento.extract_image(xref)
            largura_px = base_image["width"]
            altura_px = base_image["height"]
            rect_list = pagina.get_image_rects(xref)
            if not rect_list:
                continue
            rect = rect_list[0]
            largura_pontos = rect.width
            altura_pontos = rect.height
            largura_polegadas = largura_pontos / 72.0
            altura_polegadas = altura_pontos / 72.0
            dpi_x = round(largura_px / largura_polegadas) if largura_polegadas > 0 else 0
            dpi_y = round(altura_px / altura_polegadas) if altura_polegadas > 0 else 0
            resultados.append({
                "pagina": num_pagina + 1,
                "resolucao_px": f"{largura_px}x{altura_px}",
                "dpi_x": dpi_x,
                "dpi_y": dpi_y
            })
    documento.close()
    return resultados

# --- FUNÇÃO DE LIMPEZA CORRIGIDA ---
def limpar_arquivo():
    """Esta função será chamada quando o botão for clicado."""
    # A MUDANÇA ESTÁ AQUI: usamos 'del' em vez de '= None'
    if 'file_uploader_key' in st.session_state:
        del st.session_state['file_uploader_key']

# --- INTERFACE DA APLICAÇÃO COM STREAMLIT ---

st.set_page_config(page_title="Analisador de DPI em PDF", layout="wide")
st.title("🔎 Analisador de Resolução (DPI) de Imagens em PDF")

st.write("Faça o upload de um arquivo PDF para verificar a resolução das imagens contidas nele.")
st.markdown("---")

uploaded_file = st.file_uploader(
    "Escolha um arquivo PDF",
    type="pdf",
    key="file_uploader_key"
)

if uploaded_file is not None:
    pdf_bytes = uploaded_file.getvalue()

    with st.spinner('Analisando o PDF... Isso pode levar alguns segundos.'):
        dados_das_imagens = extrair_dpi_de_pdf(pdf_bytes)

    st.markdown("---")
    st.subheader("Resultados da Análise")

    if not dados_das_imagens:
        st.warning("Nenhuma imagem foi encontrada neste arquivo PDF.")
    else:
        st.success(f"Análise concluída! Foram encontradas {len(dados_das_imagens)} imagens.")

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown("**Página**")
        col2.markdown("**Resolução (Pixels)**")
        col3.markdown("**DPI Horizontal (X)**")
        col4.markdown("**DPI Vertical (Y)**")

        for img in dados_das_imagens:
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                col1.write(f"{img['pagina']}")
                col2.write(f"`{img['resolucao_px']}`")
                col3.metric(label="", value=f"{img['dpi_x']}")

                if img['dpi_y'] < 250:
                    col4.metric(label="", value=f"{img['dpi_y']}", delta="- Baixa Qualidade", delta_color="inverse")
                else:
                     col4.metric(label="", value=f"{img['dpi_y']}")

    st.markdown("---")
    st.button("Limpar e Iniciar Nova Análise", on_click=limpar_arquivo)
