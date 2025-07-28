"""
Módulo para geração de PDFs - Dashboard Psicologia
Funções para exportar evoluções e dados de pacientes em formato PDF
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO
import os
from flask import current_app


class PDFGenerator:
    """Classe para geração de PDFs profissionais"""
    
    def __init__(self):
        self.primary_color = HexColor('#4ECDC4')  # Verde água do site
        self.secondary_color = HexColor('#2C3E50')  # Azul escuro
        self.text_color = HexColor('#2C3E50')
        
        # Configurar estilos
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=20,
            textColor=self.secondary_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=self.primary_color,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal com justificação
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=black,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Cabeçalho
        self.styles.add(ParagraphStyle(
            name='Header',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        # Rodapé
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=grey,
            fontName='Helvetica',
            alignment=TA_CENTER
        ))

    def _draw_header_footer(self, canvas, doc):
        """Desenhar cabeçalho e rodapé personalizados"""
        canvas.saveState()
        
        # Cabeçalho
        canvas.setFillColor(self.primary_color)
        canvas.rect(0, A4[1] - 80, A4[0], 80, fill=1)
        
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 16)
        # Usar drawString com cálculo manual da posição central
        text = "Pecci Cuidado Integrado"
        text_width = canvas.stringWidth(text, 'Helvetica-Bold', 16)
        canvas.drawString((A4[0] - text_width) / 2, A4[1] - 35, text)
        
        canvas.setFont('Helvetica', 12)
        text2 = "Consultório de Psicologia"
        text2_width = canvas.stringWidth(text2, 'Helvetica', 12)
        canvas.drawString((A4[0] - text2_width) / 2, A4[1] - 55, text2)
        
        # Rodapé
        canvas.setFillColor(grey)
        canvas.setFont('Helvetica', 9)
        footer1 = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        footer1_width = canvas.stringWidth(footer1, 'Helvetica', 9)
        canvas.drawString((A4[0] - footer1_width) / 2, 30, footer1)
        
        footer2 = "Este documento contém informações confidenciais de paciente"
        footer2_width = canvas.stringWidth(footer2, 'Helvetica', 9)
        canvas.drawString((A4[0] - footer2_width) / 2, 15, footer2)
        
        canvas.restoreState()

    def gerar_pdf_evolucao(self, evolucao, paciente, psicologo):
        """
        Gerar PDF de uma evolução específica
        
        Args:
            evolucao: Objeto Evolucao do banco de dados
            paciente: Objeto Paciente relacionado
            psicologo: Objeto Doctor (psicólogo) responsável
            
        Returns:
            BytesIO: Buffer com o PDF gerado
        """
        buffer = BytesIO()
        
        # Criar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2*cm
        )
        
        # Elementos do documento
        story = []
        
        # Título
        story.append(Paragraph("EVOLUÇÃO PSICOLÓGICA", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Informações do paciente
        story.append(Paragraph("DADOS DO PACIENTE", self.styles['CustomSubtitle']))
        
        dados_paciente = [
            ["Nome:", paciente.nome_completo],
            ["Data de Nascimento:", paciente.data_nascimento.strftime('%d/%m/%Y') if paciente.data_nascimento else "Não informada"],
            ["Telefone:", paciente.telefone or "Não informado"],
            ["Email:", paciente.email or "Não informado"],
        ]
        
        table_paciente = Table(dados_paciente, colWidths=[3*cm, 12*cm])
        table_paciente.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.primary_color),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table_paciente)
        story.append(Spacer(1, 20))
        
        # Informações da sessão
        story.append(Paragraph("DADOS DA SESSÃO", self.styles['CustomSubtitle']))
        
        dados_sessao = [
            ["Data da Sessão:", evolucao.data_sessao.strftime('%d/%m/%Y')],
            ["Tipo de Sessão:", evolucao.tipo_sessao.title() if evolucao.tipo_sessao else "Individual"],
            ["Duração:", f"{evolucao.duracao_minutos} minutos" if evolucao.duracao_minutos else "50 minutos"],
            ["Psicólogo Responsável:", psicologo.name],
            ["CRP:", psicologo.crm or "Não informado"],
        ]
        
        table_sessao = Table(dados_sessao, colWidths=[3*cm, 12*cm])
        table_sessao.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.primary_color),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table_sessao)
        story.append(Spacer(1, 20))
        
        # Conteúdo da evolução
        story.append(Paragraph("EVOLUÇÃO DA SESSÃO", self.styles['CustomSubtitle']))
        
        # Descriptografar o conteúdo se necessário
        try:
            from .utils import decrypt_data
            if isinstance(evolucao.conteudo, bytes):
                conteudo = decrypt_data(evolucao.conteudo)
            else:
                conteudo = evolucao.conteudo
        except:
            conteudo = evolucao.conteudo
        
        # Dividir o conteúdo em parágrafos
        paragrafos = conteudo.split('\n')
        for paragrafo in paragrafos:
            if paragrafo.strip():
                story.append(Paragraph(paragrafo.strip(), self.styles['CustomNormal']))
                story.append(Spacer(1, 6))
        
        # Assinatura
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 50, self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>{psicologo.name}</b>", self.styles['CustomNormal']))
        story.append(Paragraph(f"CRP: {psicologo.crm or 'Não informado'}", self.styles['CustomNormal']))
        story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", self.styles['CustomNormal']))
        
        # Construir o PDF
        doc.build(story, onFirstPage=self._draw_header_footer, onLaterPages=self._draw_header_footer)
        
        buffer.seek(0)
        return buffer

    def gerar_pdf_paciente_completo(self, paciente, evolucoes, psicologo):
        """
        Gerar PDF completo do paciente com todas as evoluções
        
        Args:
            paciente: Objeto Paciente do banco de dados
            evolucoes: Lista de evoluções do paciente
            psicologo: Objeto Doctor (psicólogo) responsável
            
        Returns:
            BytesIO: Buffer com o PDF gerado
        """
        buffer = BytesIO()
        
        # Criar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2*cm
        )
        
        # Elementos do documento
        story = []
        
        # Título
        story.append(Paragraph("PRONTUÁRIO COMPLETO", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Informações completas do paciente
        story.append(Paragraph("DADOS PESSOAIS DO PACIENTE", self.styles['CustomSubtitle']))
        
        # Calcular idade se data de nascimento disponível
        idade = ""
        if paciente.data_nascimento:
            hoje = datetime.now().date()
            idade_anos = hoje.year - paciente.data_nascimento.year
            if hoje.month < paciente.data_nascimento.month or (hoje.month == paciente.data_nascimento.month and hoje.day < paciente.data_nascimento.day):
                idade_anos -= 1
            idade = f"{idade_anos} anos"
        
        dados_completos = [
            ["Nome Completo:", paciente.nome_completo],
            ["Data de Nascimento:", paciente.data_nascimento.strftime('%d/%m/%Y') if paciente.data_nascimento else "Não informada"],
            ["Idade:", idade or "Não calculada"],
            ["Telefone:", paciente.telefone or "Não informado"],
            ["Email:", paciente.email or "Não informado"],
            ["Endereço:", paciente.endereco or "Não informado"],
            ["Profissão:", paciente.profissao or "Não informada"],
            ["Estado Civil:", paciente.estado_civil or "Não informado"],
            ["Contato de Emergência:", paciente.contato_emergencia or "Não informado"],
        ]
        
        table_dados = Table(dados_completos, colWidths=[4*cm, 11*cm])
        table_dados.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.primary_color),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(table_dados)
        story.append(Spacer(1, 20))
        
        # Observações gerais
        if paciente.observacoes:
            story.append(Paragraph("OBSERVAÇÕES GERAIS", self.styles['CustomSubtitle']))
            story.append(Paragraph(paciente.observacoes, self.styles['CustomNormal']))
            story.append(Spacer(1, 20))
        
        # Resumo das sessões
        story.append(Paragraph("RESUMO DAS SESSÕES", self.styles['CustomSubtitle']))
        
        resumo_data = [["Data", "Tipo", "Duração", "Evolução (Resumo)"]]
        
        for evolucao in evolucoes:
            # Descriptografar conteúdo
            try:
                from .utils import decrypt_data
                if isinstance(evolucao.conteudo, bytes):
                    conteudo = decrypt_data(evolucao.conteudo)
                else:
                    conteudo = evolucao.conteudo
            except:
                conteudo = evolucao.conteudo
            
            # Resumir conteúdo (primeiras 100 caracteres)
            resumo_conteudo = (conteudo[:100] + "...") if len(conteudo) > 100 else conteudo
            
            resumo_data.append([
                evolucao.data_sessao.strftime('%d/%m/%Y'),
                evolucao.tipo_sessao.title() if evolucao.tipo_sessao else "Individual",
                f"{evolucao.duracao_minutos}min" if evolucao.duracao_minutos else "50min",
                resumo_conteudo
            ])
        
        if len(resumo_data) > 1:
            table_resumo = Table(resumo_data, colWidths=[2.5*cm, 2.5*cm, 2*cm, 8*cm])
            table_resumo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table_resumo)
        else:
            story.append(Paragraph("Nenhuma sessão registrada até o momento.", self.styles['CustomNormal']))
        
        # Quebra de página para evoluções detalhadas
        if evolucoes:
            story.append(PageBreak())
            story.append(Paragraph("EVOLUÇÕES DETALHADAS", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            for i, evolucao in enumerate(evolucoes):
                # Cabeçalho da evolução
                story.append(Paragraph(f"SESSÃO {i+1} - {evolucao.data_sessao.strftime('%d/%m/%Y')}", self.styles['CustomSubtitle']))
                
                # Dados da sessão
                dados_evolucao = [
                    ["Tipo:", evolucao.tipo_sessao.title() if evolucao.tipo_sessao else "Individual"],
                    ["Duração:", f"{evolucao.duracao_minutos} minutos" if evolucao.duracao_minutos else "50 minutos"],
                ]
                
                table_evolucao = Table(dados_evolucao, colWidths=[3*cm, 12*cm])
                table_evolucao.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                story.append(table_evolucao)
                story.append(Spacer(1, 10))
                
                # Conteúdo da evolução
                try:
                    from .utils import decrypt_data
                    if isinstance(evolucao.conteudo, bytes):
                        conteudo = decrypt_data(evolucao.conteudo)
                    else:
                        conteudo = evolucao.conteudo
                except:
                    conteudo = evolucao.conteudo
                
                paragrafos = conteudo.split('\n')
                for paragrafo in paragrafos:
                    if paragrafo.strip():
                        story.append(Paragraph(paragrafo.strip(), self.styles['CustomNormal']))
                        story.append(Spacer(1, 4))
                
                # Espaçamento entre evoluções
                if i < len(evolucoes) - 1:
                    story.append(Spacer(1, 20))
                    story.append(Paragraph("_" * 80, self.styles['CustomNormal']))
                    story.append(Spacer(1, 20))
        
        # Assinatura final
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 50, self.styles['CustomNormal']))
        story.append(Paragraph(f"<b>{psicologo.name}</b>", self.styles['CustomNormal']))
        story.append(Paragraph(f"CRP: {psicologo.crm or 'Não informado'}", self.styles['CustomNormal']))
        story.append(Paragraph(f"Data de emissão: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", self.styles['CustomNormal']))
        
        # Construir o PDF
        doc.build(story, onFirstPage=self._draw_header_footer, onLaterPages=self._draw_header_footer)
        
        buffer.seek(0)
        return buffer


# Instância global para uso nas rotas
pdf_generator = PDFGenerator()
