import os
import io
import re
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

# ==============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO E BANCO DE DADOS
# ==============================================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_projeto_atestados_rh_2026'

# Configuração de upload de arquivos
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuração do banco de dados SQLite
db_path = os.path.join(app.root_path, 'database', 'atestados.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==============================================================================
# MODELO DO BANCO DE DADOS (ORM)
# ==============================================================================
class Atestado(db.Model):
    __tablename__ = 'atestados'
    
    id = db.Column(db.Integer, primary_key=True)
    colaborador = db.Column(db.String(100), nullable=False)
    loja = db.Column(db.String(50), nullable=False)
    setor = db.Column(db.String(50), nullable=False)
    medico = db.Column(db.String(100), nullable=True)
    crm = db.Column(db.String(20), nullable=True)
    status_crm = db.Column(db.String(20), default='Ativo')
    cid = db.Column(db.String(10), nullable=False)
    cnpj = db.Column(db.String(20), nullable=True)
    dias_afastamento = db.Column(db.Integer, nullable=False)
    caminho_imagem = db.Column(db.String(255), nullable=True)
    data_registro = db.Column(db.DateTime, default=datetime.now)

# Cria as tabelas automaticamente na inicialização
with app.app_context():
    db.create_all()

# ==============================================================================
# ROTAS DO SISTEMA
# ==============================================================================

@app.route('/')
def login():
    """Tela de Autenticação (RF01/RF02)"""
    return render_template('login.html')

@app.route('/scanner')
def scanner():
    """Tela de Captura por Câmera e OCR (RF04/RF05/RF08)"""
    return render_template('scanner.html')

@app.route('/processar-ocr', methods=['POST'])
def processar_ocr():
    """
    Simulação/Processamento do Motor OCR com tratamento por Regex (RF06/RF07/RF09)
    """
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    # Renomeia o arquivo com UUID para segurança (RNF07)
    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Lógica de OCR / Extração de dados simulada para pré-preenchimento
    dados_extraidos = {
        'colaborador': '',
        'medico': 'Dr. Carlos Silva',
        'crm': '123456-SP',
        'cid': 'J06',
        'cnpj': '12.345.678/0001-90',
        'dias_afastamento': 3,
        'caminho_imagem': filename
    }
    return jsonify(dados_extraidos)

@app.route('/salvar-atestado', methods=['POST'])
def salvar_atestado():
    """Salva o registro confirmado no Banco de Dados (RF12)"""
    try:
        novo_atestado = Atestado(
            colaborador=request.form.get('colaborador'),
            loja=request.form.get('loja'),
            setor=request.form.get('setor'),
            medico=request.form.get('medico'),
            crm=request.form.get('crm'),
            cid=request.form.get('cid'),
            cnpj=request.form.get('cnpj'),
            dias_afastamento=int(request.form.get('dias_afastamento', 1)),
            caminho_imagem=request.form.get('caminho_imagem')
        )
        db.session.add(novo_atestado)
        db.session.commit()
        flash('Atestado cadastrado com sucesso!', 'success')
        return redirect(url_for('base_dados'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar registro: {str(e)}', 'error')
        return redirect(url_for('scanner'))

@app.route('/base-dados')
def base_dados():
    """Exibe o Histórico de Atestados com Tabela Dinâmica (RF13)"""
    registros = Atestado.query.order_by(Atestado.data_registro.desc()).all()
    return render_template('base_dados.html', registros=registros)

@app.route('/exportar-excel', methods=['POST'])
def exportar_excel():
    """
    Exportação Avançada para Excel com Filtros e Multi-Abas via Pandas (RF14.1/RF14.2/RF14.3)
    """
    loja_filtro = request.form.get('loja')
    setor_filtro = request.form.get('setor')
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    cid_filtro = request.form.get('cid')

    query = Atestado.query

    if loja_filtro and loja_filtro != 'TODAS':
        query = query.filter(Atestado.loja == loja_filtro)
    if setor_filtro and setor_filtro != 'TODOS':
        query = query.filter(Atestado.setor == setor_filtro)
    if cid_filtro:
        query = query.filter(Atestado.cid.like(f"%{cid_filtro}%"))
    if data_inicio and data_fim:
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        fim = datetime.strptime(data_fim, '%Y-%m-%d')
        query = query.filter(Atestado.data_registro.between(inicio, fim))

    registros = query.all()

    if not registros:
        flash('Nenhum registro encontrado para os filtros informados.', 'warning')
        return redirect(url_for('base_dados'))

    # Aba 1: Detalhado
    dados_detalhados = [{
        'ID Registro': a.id,
        'Colaborador': a.colaborador,
        'Loja': a.loja,
        'Setor': a.setor,
        'Médico': a.medico,
        'CRM': a.crm,
        'Status CRM': a.status_crm,
        'CID-10': a.cid,
        'CNPJ Clínica': a.cnpj,
        'Dias Afastados': a.dias_afastamento,
        'Data de Registro': a.data_registro.strftime('%d/%m/%Y %H:%M')
    } for a in registros]

    df_detalhado = pd.DataFrame(dados_detalhados)

    # Aba 2: Resumo Executivo
    resumo_loja = df_detalhado.groupby('Loja').agg(
        Total_Atestados=('ID Registro', 'count'),
        Total_Dias_Perdidos=('Dias Afastados', 'sum')
    ).reset_index()

    resumo_cid = df_detalhado['CID-10'].value_counts().head(5).reset_index()
    resumo_cid.columns = ['CID-10', 'Quantidade']

    # Geração do arquivo em memória (BytesIO)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_detalhado.to_excel(writer, sheet_name='Atestados Detalhados', index=False)
        resumo_loja.to_excel(writer, sheet_name='Resumo Executivo', startrow=0, index=False)
        resumo_cid.to_excel(writer, sheet_name='Resumo Executivo', startrow=len(resumo_loja) + 4, index=False)

        # Ajuste de largura das colunas
        worksheet = writer.sheets['Atestados Detalhados']
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    output.seek(0)
    nome_arquivo = f"Relatorio_Atestados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=nome_arquivo
    )

@app.route('/dashboard')
def dashboard():
    """Exibe o Dashboard do Power BI Embedded (RF15/RF16)"""
    return render_template('dashboard.html')

# ==============================================================================
# EXECUÇÃO DO SERVIDOR
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)