# PR: Feedback + IA (aprendizado com rótulos)

Este pacote adiciona:
- Endpoint `/feedback` para registrar rótulos/correções.
- Endpoint `/train` para treinar um modelo leve (SGDRegressor).
- Blending IA + hedônico no `assessor.py` (40% IA / 60% hedônico no P50).
- UI (Streamlit) com botões de feedback e botão “Treinar agora”.

## Como aplicar no seu repositório

1) Faça backup ou crie um branch:
   ```bash
   git checkout -b feature/feedback-ai
   ```

2) Copie os arquivos deste pacote para a raiz do seu projeto, preservando estrutura.

3) Instale dependências adicionais (se faltarem):
   ```bash
   pip install scikit-learn joblib requests
   ```

4) Rode local:
   ```bash
   uvicorn app.main:app --reload --port 8000
   streamlit run streamlit_app.py
   ```

5) Commit e push:
   ```bash
   git add .
   git commit -m "feat: feedback + IA (endpoints, treino e UI)"
   git push -u origin feature/feedback-ai
   ```

6) Abra um Pull Request no GitHub desse branch para `main`.
