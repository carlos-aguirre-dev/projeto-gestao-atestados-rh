# 🏥 Sistema de Gestão de Atestados Médicos - RH Analytics

Uma aplicação web completa desenvolvida para automatizar o recebimento, triagem (OCR) e controle de atestados médicos no departamento de Recursos Humanos.

## 🚀 Funcionalidades Principais

- **Captura Inteligente:** Leitura de atestados via webcam em tempo real com animação visual de scanner ou upload de arquivos.
- **Simulação de OCR:** Extração automática de dados do documento (Médico, CRM, CID-10, CNPJ e Dias de Afastamento).
- **Validação Human-in-the-Loop:** Interface para conferência e ajuste manual dos dados pelo time de RH antes da gravação.
- **Persistência de Dados:** Armazenamento seguro utilizando SQLite e SQLAlchemy.
- **Relatórios Automatizados:** Exportação em Excel (`.xlsx`) com relatório detalhado e resumo executivo via Pandas.
- **Dashboard Integrado:** Estrutura pronta para incorporação de relatórios interativos do Power BI.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, Flask, SQLAlchemy, Pandas, OpenPyXL
- **Frontend:** HTML5, JavaScript (WebRTC / MediaDevices), Tailwind CSS, FontAwesome
- **Banco de Dados:** SQLite

## 🔧 Como Executar o Projeto Localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU_USUARIO/projeto-gestao-atestados-rh.git](https://github.com/SEU_USUARIO/projeto-gestao-atestados-rh.git)
   cd projeto-gestao-atestados-rh