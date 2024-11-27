import sys
import os
import re
import unicodedata
import shutil
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QLabel,
    QFileDialog, QDialog, QComboBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette


# Lista de stopwords em Português e Inglês, incluindo artigos, pronomes, adjetivos, verbos, números, numerais
STOPWORDS = {
    # Artigos em Português
    'a', 'à', 'as', 'ao', 'aos', 'um', 'uma', 'uns', 'umas',
    'o', 'os', 'da', 'das', 'do', 'dos', 'de', 'em', 'para',
    'por', 'com', 'sem', 'sobre', 'entre', 'até', 'desde',
    'pela', 'pelas', 'pelo', 'pelos',

    # Artigos em Inglês
    'a', 'an', 'the',

    # Pronomes em Português
    'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas',
    'me', 'te', 'se', 'nos', 'vos', 'lhe', 'lhes',
    'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
    'aquele', 'aquela', 'aqueles', 'aquelas',

    # Pronomes em Inglês
    'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'me', 'him', 'her', 'us', 'them',
    'this', 'that', 'these', 'those',

    # Preposições e Conjunções em Português
    'que', 'como', 'se', 'mais', 'menos', 'também', 'sempre',
    'quando', 'onde', 'porque', 'para', 'com', 'sem', 'sobre',
    'entre', 'até', 'desde',

    # Preposições e Conjunções em Inglês
    'and', 'or', 'but', 'because', 'as', 'until', 'while',
    'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after',

    # Adjetivos Comuns em Português
    'grande', 'pequeno', 'bom', 'ruim', 'novo', 'velho',
    'primeiro', 'último', 'melhor', 'pior',

    # Adjetivos Comuns em Inglês
    'big', 'small', 'good', 'bad', 'new', 'old',
    'first', 'last', 'better', 'worse',

    # Verbos Comuns em Português
    'ser', 'estar', 'ter', 'fazer', 'poder', 'dizer',
    'ir', 'ver', 'dar', 'saber', 'querer', 'chegar',
    'passar', 'dever', 'ficar', 'contar', 'começar',

    # Verbos Comuns em Inglês
    'be', 'have', 'do', 'say', 'go', 'see', 'get',
    'make', 'know', 'think', 'take', 'come', 'want',
    'look', 'use', 'find', 'give', 'tell', 'work',

    # Números e Numerais em Português
    'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete',
    'oito', 'nove', 'dez', 'primeiro', 'segundo', 'terceiro',
    'quarto', 'quinto',

    # Números e Numerais em Inglês
    'one', 'two', 'three', 'four', 'five', 'six', 'seven',
    'eight', 'nine', 'ten', 'first', 'second', 'third',
    'fourth', 'fifth',

    # Preposição 'x' usada como 'versus' em Português
    'x',
}

def remover_acentos(texto):
    """
    Remove acentos de uma string.
    """
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

def extrair_palavras(nome_arquivo):
    """
    Extrai palavras significativas do nome do arquivo, removendo stopwords e acentos.
    Retorna um conjunto de palavras em minúsculas sem acentos.
    """
    nome_sem_ext = os.path.splitext(nome_arquivo)[0]
    palavras = re.split(r'\W+', nome_sem_ext)
    palavras_normalizadas = set(
        remover_acentos(palavra.lower())
        for palavra in palavras
        if palavra and remover_acentos(palavra.lower()) not in STOPWORDS
    )
    return palavras_normalizadas

# Dicionário de traduções para as duas línguas suportadas
LANGUAGES = {
    'english': {
        'window_title': "Markdown Merge App",
        'instruction': "Select the files you want to merge or delete.",
        'button_delete': "Delete",
        'button_undo': "Undo",
        'button_merge': "Merge",
        'feedback_deleted': "Deleted files: {files}",
        'feedback_merged': "Merged into: {filename}",
        'feedback_undone': "Action undone: {action}",
        'error_no_files_selected': "No files selected.",
        'error_merge_failed': "Error merging files: {error}",
        'error_delete_failed': "Error deleting files: {error}",
        'merge_dialog_title': "New Merged File Name",
        'merge_dialog_instruction': "Select a suggested name or enter a new name for the merged file:",
        'merge_dialog_ok': "OK",
        'merge_dialog_cancel': "Cancel",
        'warning_no_files_selected_delete': "No files selected to delete.",
        'warning_no_files_selected_merge': "No files selected to merge.",
        'info_no_common_words': "No common words found for merging.",
        'language_selection_title': "Select Language",
        'language_selection_instruction': "Choose the application language:",
        'language_english': "English",
        'language_portuguese': "Portuguese (Brazilian)",
    },
    'portuguese': {
        'window_title': "Aplicativo de Mesclagem de Markdown",
        'instruction': "Selecione os arquivos que deseja mesclar ou apagar.",
        'button_delete': "Apagar",
        'button_undo': "Desfazer",
        'button_merge': "Mesclar",
        'feedback_deleted': "Arquivos apagados: {files}",
        'feedback_merged': "Arquivos mesclados em: {filename}",
        'feedback_undone': "Ação desfeita: {action}",
        'error_no_files_selected': "Nenhum arquivo selecionado.",
        'error_merge_failed': "Erro ao mesclar arquivos: {error}",
        'error_delete_failed': "Erro ao apagar arquivos: {error}",
        'merge_dialog_title': "Nome do Novo Arquivo Mesclado",
        'merge_dialog_instruction': "Selecione um nome sugerido ou digite um novo nome para o arquivo mesclado:",
        'merge_dialog_ok': "OK",
        'merge_dialog_cancel': "Cancelar",
        'warning_no_files_selected_delete': "Nenhum arquivo selecionado para apagar.",
        'warning_no_files_selected_merge': "Nenhum arquivo selecionado para mesclar.",
        'info_no_common_words': "Nenhuma palavra comum encontrada para mesclagem.",
        'language_selection_title': "Selecione o Idioma",
        'language_selection_instruction': "Escolha o idioma do aplicativo:",
        'language_english': "Inglês",
        'language_portuguese': "Português (Brasil)",
    }
}

class LanguageSelectionDialog(QDialog):
    """
    Diálogo para seleção de idioma ao iniciar a aplicação.
    """
    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.translations = translations
        self.setWindowTitle(self.translations['language_selection_title'])
        self.setModal(True)
        self.selected_language = 'english'  # Default
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Instruções
        instrucao = QLabel(self.translations['language_selection_instruction'])
        instrucao.setFont(QFont("Arial", 12))
        layout.addWidget(instrucao)

        # ComboBox para seleção de idioma
        self.combo_languages = QComboBox()
        self.combo_languages.addItem(self.translations['language_english'], 'english')
        self.combo_languages.addItem(self.translations['language_portuguese'], 'portuguese')
        self.combo_languages.setCurrentIndex(0)  # Default to English
        layout.addWidget(self.combo_languages)

        # Botões de confirmação e cancelamento
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_selected_language(self):
        return self.combo_languages.currentData()

class NameSuggestionDialog(QDialog):
    """
    Diálogo personalizado para sugerir nomes de arquivos e permitir edição.
    Utiliza um QComboBox para apresentar sugestões de nomes baseados nos arquivos a serem mesclados.
    """
    def __init__(self, suggested_names, translations, parent=None):
        super().__init__(parent)
        self.translations = translations
        self.setWindowTitle(self.translations['merge_dialog_title'])
        self.setModal(True)
        self.suggested_names = suggested_names
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Instruções
        instrucao = QLabel(self.translations['merge_dialog_instruction'])
        instrucao.setFont(QFont("Arial", 12))
        layout.addWidget(instrucao)

        # ComboBox com sugestões
        self.combo_sugestoes = QComboBox()
        self.combo_sugestoes.addItems(self.suggested_names)
        self.combo_sugestoes.setEditable(True)
        layout.addWidget(self.combo_sugestoes)

        # Botões de confirmação e cancelamento
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText(self.translations['merge_dialog_ok'])
        buttons.button(QDialogButtonBox.Cancel).setText(self.translations['merge_dialog_cancel'])
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_nome(self):
        return self.combo_sugestoes.currentText()

class MergeMDApp(QWidget):
    def __init__(self, translations):
        super().__init__()
        self.translations = translations
        self.setWindowTitle(self.translations['window_title'])
        self.setGeometry(100, 100, 1400, 800)
        self.palavras_puladas = set()
        self.action_history = []  # Histórico de ações para desfazer
        self.initUI()

    def initUI(self):
        # Aplicar tema escuro
        self.set_dark_theme()

        layout = QVBoxLayout()

        # Instruções
        instrucao = QLabel(self.translations['instruction'])
        instrucao.setFont(QFont("Arial", 14))
        instrucao.setStyleSheet("color: white;")
        layout.addWidget(instrucao)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Freq.", "Palavra", "Arquivos"])
        self.tree.setColumnWidth(0, 50)  # Frequência
        self.tree.setColumnWidth(1, 300)  # Palavra
        self.tree.setColumnWidth(2, 1000)  # Arquivos
        self.tree.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.tree.setSelectionMode(QTreeWidget.NoSelection)
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)  # Mostrar setas para expandir

        layout.addWidget(self.tree)

        # Botões
        button_layout = QHBoxLayout()

        self.btn_delete = QPushButton(self.translations['button_delete'])
        self.btn_delete.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.btn_delete.clicked.connect(self.apagar_arquivos)
        button_layout.addWidget(self.btn_delete)

        self.btn_undo = QPushButton(self.translations['button_undo'])
        self.btn_undo.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_undo.setStyleSheet("""
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """)
        self.btn_undo.clicked.connect(self.desfazer_acao)
        button_layout.addWidget(self.btn_undo)

        self.btn_merge = QPushButton(self.translations['button_merge'])
        self.btn_merge.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_merge.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)
        self.btn_merge.clicked.connect(self.merge_arquivos)
        button_layout.addWidget(self.btn_merge)

        layout.addLayout(button_layout)

        # Feedback Label
        self.feedback = QLabel("")
        self.feedback.setFont(QFont("Arial", 12))
        self.feedback.setStyleSheet("color: #28a745;")
        layout.addWidget(self.feedback)

        self.setLayout(layout)

        # Carregar arquivos
        self.carregar_arquivos()

    def set_dark_theme(self):
        """
        Aplica um tema escuro à aplicação.
        """
        dark_palette = QPalette()

        # Definições de cores
        dark_palette.setColor(QPalette.Window, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)

        # Links
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        QApplication.instance().setPalette(dark_palette)
        QApplication.instance().setStyle("Fusion")

    def carregar_arquivos(self):
        """
        Abre um diálogo para selecionar a pasta e carrega os arquivos .md.
        """
        # Abrir um diálogo para selecionar a pasta
        diretorio = QFileDialog.getExistingDirectory(self, "Select folder with .md files" if self.translations['language_english'] == "English" else "Selecione a pasta com arquivos .md")
        if not diretorio:
            QMessageBox.warning(self, "Warning" if self.translations['language_english'] == "English" else "Aviso", 
                                self.translations['error_no_files_selected'] if self.translations['language_english'] == "English" else "Nenhuma pasta selecionada. O aplicativo será fechado.")
            sys.exit()

        # Listar todos os arquivos .md na pasta
        arquivos_md = [f for f in os.listdir(diretorio) if f.lower().endswith('.md')]

        if not arquivos_md:
            QMessageBox.warning(self, "Warning" if self.translations['language_english'] == "English" else "Aviso",
                                self.translations['info_no_common_words'] if self.translations['language_english'] == "English" else "Nenhuma palavra comum encontrada para mesclagem.")
            sys.exit()

        # Agrupar arquivos por palavras comuns
        palavra_para_arquivos = defaultdict(list)
        for arquivo in arquivos_md:
            palavras = extrair_palavras(arquivo)
            for palavra in palavras:
                palavra_para_arquivos[palavra].append(arquivo)

        # Remover palavras que aparecem apenas em um arquivo
        palavra_para_arquivos = {k: v for k, v in palavra_para_arquivos.items() if len(v) > 1}

        if not palavra_para_arquivos:
            QMessageBox.information(self, "Information" if self.translations['language_english'] == "English" else "Informação",
                                    self.translations['info_no_common_words'] if self.translations['language_english'] == "English" else "Nenhuma palavra comum encontrada para mesclagem.")
            sys.exit()

        # Ordenar as palavras por frequência (número de arquivos que contêm a palavra) decrescente
        palavra_ordenada = sorted(palavra_para_arquivos.items(), key=lambda x: len(x[1]), reverse=True)

        # Adicionar ao Tree Widget
        for palavra, arquivos in palavra_ordenada:
            if palavra in self.palavras_puladas:
                continue
            palavra_item = QTreeWidgetItem([str(len(arquivos)), palavra, ""])
            palavra_item.setFont(1, QFont("Arial", 12, QFont.Bold))
            palavra_item.setForeground(1, QColor(255, 255, 255))
            for arquivo in arquivos:
                arquivo_item = QTreeWidgetItem(["", "", arquivo])
                arquivo_item.setCheckState(2, Qt.Unchecked)
                palavra_item.addChild(arquivo_item)
            self.tree.addTopLevelItem(palavra_item)

        self.diretorio = diretorio

    def obter_arquivos_selecionados(self):
        """
        Retorna uma lista de todos os arquivos que estão checados.
        """
        arquivos = []
        for i in range(self.tree.topLevelItemCount()):
            top_item = self.tree.topLevelItem(i)
            for j in range(top_item.childCount()):
                child = top_item.child(j)
                if child.checkState(2) == Qt.Checked:
                    arquivos.append(child.text(2))
        return arquivos

    def apagar_arquivos(self):
        """
        Envia os arquivos selecionados para a lixeira (backup) e remove da árvore.
        """
        arquivos = self.obter_arquivos_selecionados()
        if not arquivos:
            QMessageBox.warning(self, 
                                "Warning" if self.translations['language_english'] == "English" else "Aviso", 
                                self.translations['warning_no_files_selected_delete'])
            return

        # Criar diretório de backup se não existir
        backup_dir = os.path.join(self.diretorio, ".backup_merge_md")
        os.makedirs(backup_dir, exist_ok=True)

        try:
            for arquivo in arquivos:
                src = os.path.join(self.diretorio, arquivo)
                dest = os.path.join(backup_dir, arquivo)
                shutil.move(src, dest)

            # Atualizar a árvore de arquivos
            for arquivo in arquivos:
                self.remover_arquivo_da_arvore(arquivo)

            # Adicionar ação ao histórico para desfazer
            self.action_history.append({
                'tipo': 'apagar',
                'arquivos': arquivos
            })

            feedback_msg = self.translations['feedback_deleted'].format(files=", ".join(arquivos))
            self.feedback.setText(feedback_msg)
        except Exception as e:
            error_msg = self.translations['error_delete_failed'].format(error=str(e))
            QMessageBox.critical(self, 
                                 "Error" if self.translations['language_english'] == "English" else "Erro", 
                                 error_msg)

    def desfazer_acao(self):
        """
        Desfaz a última ação realizada (merge ou apagar).
        """
        if not self.action_history:
            QMessageBox.information(self, 
                                     "Information" if self.translations['language_english'] == "English" else "Informação", 
                                     "No action to undo." if self.translations['language_english'] == "English" else "Nenhuma ação para desfazer.")
            return

        ultima_acao = self.action_history.pop()

        backup_dir = os.path.join(self.diretorio, ".backup_merge_md")

        try:
            if ultima_acao['tipo'] == 'apagar':
                # Restaurar arquivos apagados
                for arquivo in ultima_acao['arquivos']:
                    src = os.path.join(backup_dir, arquivo)
                    dest = os.path.join(self.diretorio, arquivo)
                    shutil.move(src, dest)
                    self.adicionar_arquivo_na_arvore(arquivo)

                action_text = "Delete files" if self.translations['language_english'] == "English" else "Apagar arquivos"
                feedback_msg = self.translations['feedback_undone'].format(action=action_text)
                self.feedback.setText(feedback_msg)
            
            elif ultima_acao['tipo'] == 'merge':
                # Desfazer merge: deletar arquivo mesclado e restaurar originais
                merged_file = ultima_acao['merged_file']
                orig_files = ultima_acao['orig_files']

                # Deletar o arquivo mesclado
                merged_path = os.path.join(self.diretorio, merged_file)
                if os.path.exists(merged_path):
                    os.remove(merged_path)

                # Restaurar arquivos originais do backup
                for arquivo in orig_files:
                    src = os.path.join(backup_dir, arquivo)
                    dest = os.path.join(self.diretorio, arquivo)
                    shutil.move(src, dest)
                    self.adicionar_arquivo_na_arvore(arquivo)

                action_text = "Merge files" if self.translations['language_english'] == "English" else "Mesclar arquivos"
                feedback_msg = self.translations['feedback_undone'].format(action=action_text)
                self.feedback.setText(feedback_msg)
            
            else:
                QMessageBox.warning(self, 
                                    "Warning" if self.translations['language_english'] == "English" else "Aviso", 
                                    "Unknown action type." if self.translations['language_english'] == "English" else "Tipo de ação desconhecido.")
                return

        except Exception as e:
            error_msg = self.translations['error_merge_failed'].format(error=str(e))
            QMessageBox.critical(self, 
                                 "Error" if self.translations['language_english'] == "English" else "Erro", 
                                 error_msg)

    def merge_arquivos(self):
        """
        Mescla os arquivos selecionados em um novo arquivo e apaga os originais.
        Se o nome do novo arquivo já existir, substitui pelo novo.
        """
        arquivos = self.obter_arquivos_selecionados()
        if not arquivos:
            QMessageBox.warning(self, 
                                "Warning" if self.translations['language_english'] == "English" else "Aviso", 
                                self.translations['warning_no_files_selected_merge'])
            return

        # Gerar nomes sugeridos baseados nos arquivos a serem mesclados
        nomes_sem_ext = [os.path.splitext(f)[0] for f in arquivos]
        nome_sugerido = " + ".join(nomes_sem_ext)

        # Iniciar o diálogo de sugestão de nome
        dialog = NameSuggestionDialog([nome_sugerido] + nomes_sem_ext, self.translations, self)
        if dialog.exec_() == QDialog.Accepted:
            novo_nome = dialog.get_nome().strip()
            if not novo_nome:
                QMessageBox.warning(self, 
                                    "Warning" if self.translations['language_english'] == "English" else "Aviso", 
                                    self.translations['error_no_files_selected'] if self.translations['language_english'] == "English" else "Nome do arquivo inválido.")
                return

            # Garantir que o nome do arquivo termine com .md
            if not novo_nome.lower().endswith('.md'):
                novo_nome += '.md'

            # Caminho completo para o novo arquivo
            caminho_novo = os.path.join(self.diretorio, novo_nome)

            # Se o arquivo já existir, substituir
            if os.path.exists(caminho_novo):
                try:
                    os.remove(caminho_novo)
                except Exception as e:
                    error_msg = self.translations['error_merge_failed'].format(error=str(e))
                    QMessageBox.critical(self, 
                                         "Error" if self.translations['language_english'] == "English" else "Erro", 
                                         error_msg)
                    return

            # Criar diretório de backup se não existir
            backup_dir = os.path.join(self.diretorio, ".backup_merge_md")
            os.makedirs(backup_dir, exist_ok=True)

            try:
                # Mesclar conteúdos
                with open(caminho_novo, 'w', encoding='utf-8') as dest:
                    for arquivo in arquivos:
                        src = os.path.join(self.diretorio, arquivo)
                        with open(src, 'r', encoding='utf-8') as src_file:
                            conteudo = src_file.read()
                            dest.write(f"## {arquivo}\n\n")
                            dest.write(conteudo)
                            dest.write("\n\n")

                # Mover arquivos originais para backup
                for arquivo in arquivos:
                    src = os.path.join(self.diretorio, arquivo)
                    dest = os.path.join(backup_dir, arquivo)
                    shutil.move(src, dest)
                    self.remover_arquivo_da_arvore(arquivo)

                # Adicionar ação ao histórico para desfazer
                self.action_history.append({
                    'tipo': 'merge',
                    'merged_file': novo_nome,
                    'orig_files': arquivos
                })

                feedback_msg = self.translations['feedback_merged'].format(filename=novo_nome)
                self.feedback.setText(feedback_msg)
            except Exception as e:
                error_msg = self.translations['error_merge_failed'].format(error=str(e))
                QMessageBox.critical(self, 
                                     "Error" if self.translations['language_english'] == "English" else "Erro", 
                                     error_msg)

    def remover_arquivo_da_arvore(self, arquivo):
        """
        Remove um arquivo específico da árvore.
        """
        for i in range(self.tree.topLevelItemCount()):
            top_item = self.tree.topLevelItem(i)
            for j in range(top_item.childCount()):
                child = top_item.child(j)
                if child.text(2) == arquivo:
                    top_item.removeChild(child)
                    # Atualizar a frequência
                    freq = int(top_item.text(0)) - 1
                    top_item.setText(0, str(freq))
                    break

    def adicionar_arquivo_na_arvore(self, arquivo):
        """
        Adiciona um arquivo específico de volta à árvore.
        """
        palavras = extrair_palavras(arquivo)
        for palavra in palavras:
            # Encontrar o item correspondente à palavra
            encontrado = False
            for i in range(self.tree.topLevelItemCount()):
                top_item = self.tree.topLevelItem(i)
                if top_item.text(1) == palavra:
                    # Adicionar o arquivo como filho
                    arquivo_item = QTreeWidgetItem(["", "", arquivo])
                    arquivo_item.setCheckState(2, Qt.Unchecked)
                    top_item.addChild(arquivo_item)
                    # Atualizar a frequência
                    freq = int(top_item.text(0)) + 1
                    top_item.setText(0, str(freq))
                    encontrado = True
                    break
            if not encontrado and palavra not in self.palavras_puladas:
                # Adicionar nova palavra na árvore
                freq = 1
                palavra_item = QTreeWidgetItem([str(freq), palavra, ""])
                palavra_item.setFont(1, QFont("Arial", 12, QFont.Bold))
                palavra_item.setForeground(1, QColor(255, 255, 255))
                arquivo_item = QTreeWidgetItem(["", "", arquivo])
                arquivo_item.setCheckState(2, Qt.Unchecked)
                palavra_item.addChild(arquivo_item)
                self.tree.addTopLevelItem(palavra_item)

def main():
    app = QApplication(sys.argv)

    # Criar e exibir o diálogo de seleção de idioma
    temp_translations = LANGUAGES['english']  # Default to English for the selection dialog
    selection_dialog = LanguageSelectionDialog(temp_translations, None)
    if selection_dialog.exec_() == QDialog.Accepted:
        selected_language = selection_dialog.get_selected_language()
    else:
        # Se o usuário cancelar, fechar a aplicação
        sys.exit()

    # Obter as traduções baseadas na seleção
    translations = LANGUAGES.get(selected_language, LANGUAGES['english'])

    # Inicializar a aplicação principal com as traduções selecionadas
    ex = MergeMDApp(translations)
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
