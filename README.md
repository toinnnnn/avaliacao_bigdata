# 🎶 Projeto Big Data - Spotify & YouTube

Este projeto tem como objetivo **extrair, transformar e analisar dados do Spotify e do YouTube**, integrando-os em um **pipeline ETL** com visualização em um **dashboard interativo no Streamlit**.

---

## 📂 Estrutura de Pastas

```
project/
│── docs/                  # Documentação do projeto
│── notebooks/             # Notebooks auxiliares (exploração inicial, testes)
│── src/                   # Código-fonte principal
│   ├── dashboard/         
│   │   └── app_streamlit.py     # Dashboard interativo
│   ├── db/                
│   │   ├── init.sql             # Script inicial do banco
│   │   └── schema.sql           # Estrutura das tabelas
│   ├── extract_spotify.py       # Extração de dados Spotify
│   ├── extract_youtube.py       # Extração de dados YouTube
│   ├── transform.py             # Transformações e correlação
│   ├── load.py                  # Carregamento no banco
│   ├── etl_runner.py            # Orquestração do ETL
│   ├── test_spotify.py          # Testes unitários Spotify
│   └── tests.py                 # Testes gerais
│
│── .env                  # Variáveis de ambiente (chaves API, DB, etc.)
│── requirements.txt       # Dependências do projeto
│── README.md              # Documentação principal
│── spotify_tracks.csv     # Dump exportado do Spotify
│── youtube_videos.csv     # Dump exportado do YouTube
│── correlations.csv       # Dump exportado de correlações
```

---

## ⚙️ Pipeline ETL

Fluxo do processo:

**Spotify API / YouTube API → Extração → Transformação (limpeza, normalização, correlação) → PostgreSQL → Streamlit Dashboard**

📌 **Fluxograma:**

1. **Extração**

   * Spotify: Playlists *Top 50* (Global, BR, US, MX, PT).
   * YouTube: *Most Popular Videos* (BR, US, MX, PT).

2. **Transformação**

   * Padronização dos dados (datas, nomes, normalização).
   * Tratamento de valores nulos.
   * Cálculo de métricas derivadas (duração média, popularidade, engajamento).
   * Correlação entre músicas (Spotify) e vídeos (YouTube) via **fuzzy matching** (RapidFuzz).

3. **Carga**

   * Dados salvos no PostgreSQL em tabelas:

     * `spotify_tracks`
     * `youtube_videos`
     * `correlations`

4. **Visualização**

   * Dashboard no **Streamlit**, integrando Spotify & YouTube.

---

## 📊 Dashboard Interativo

O dashboard possui filtros laterais:

* 🌍 **Regiões** (BR, MX, PT, US, GLOBAL)
* 📅 **Intervalo de Anos**
* 🎤 **Artistas Spotify**
* 🔥 **Popularidade Spotify**
* 📺 **Categorias YouTube**
* 📡 **Canais YouTube**

### Seções do Dashboard

1. **🎧 Análise no Spotify**

   * Distribuição de popularidade por artista.
   * Duração média das músicas.
   * Top artistas.

2. **📺 Análise no YouTube**

   * Views totais por categoria.
   * Engajamento (likes e comentários).
   * Top canais.

3. **🌍 Comparativo por Região**

   * Popularidade média no Spotify por país.
   * Views totais no YouTube por país.

4. **🔗 Correlação Spotify x YouTube**

   * Scatter plot: Popularidade (Spotify) x Views (YouTube).
   * Boxplot: Distribuição de views por faixas de popularidade.
   * Barras agrupadas: Média de views em faixas de popularidade.

---

## 🧪 Testes

Foram criados testes unitários básicos para garantir a consistência:

* **Spotify**

  * Verificação de colunas obrigatórias (`track_id`, `track_name`, `artist_name`, `popularity`).
  * Checagem de valores nulos.

* **YouTube**

  * Verificação de colunas obrigatórias (`video_id`, `title`, `view_count`, `category`).
  * Checagem de valores nulos.

* **Correlação**

  * Teste de existência das colunas (`track_name`, `video_title`, `similarity_score`).
  * Verificação se o score de similaridade está no intervalo 0–100.

Execução dos testes:

```bash
python src/tests.py
```

---

## 🚀 Como Executar

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/avaliacao_bigdata.git
cd avaliacao_bigdata
```

### 2. Criar Ambiente Virtual

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar `.env`

Defina as variáveis:

```
SPOTIFY_CLIENT_ID=xxxx
SPOTIFY_CLIENT_SECRET=xxxx
YOUTUBE_API_KEY=xxxx
DB_HOST=localhost
DB_PORT=5432
DB_NAME=spotify_youtube
DB_USER=postgres
DB_PASSWORD=postgres
```

### 5. Rodar ETL

```bash
python src/etl_runner.py
```

### 6. Rodar Dashboard

```bash
streamlit run src/dashboard/app_streamlit.py
```

---

## 📌 Conclusão

Este projeto integra dados musicais (Spotify) e de vídeos (YouTube) para permitir **análises comparativas entre popularidade e engajamento**.
Com o ETL desenvolvido e o dashboard interativo, é possível identificar padrões de consumo por região, tendências culturais e relações entre músicas e vídeos virais.

---

## 👨‍💻 Autores

* **Antônio Vinícius**
* **Douglas Lucas**
* **Matheus Ramos**
* – Desenvolvimento do ETL e Dashboard
* Atividade acadêmica de Big Data — 2025
