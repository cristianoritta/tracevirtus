
import re
from Lib.Functions.CriarDicionarioMovimentacoes import iniciar_informacoes_creditos_debitos, limpar_valor
from Lib.Functions.Numeros import apenas_numeros

class Plugin:
    
    def __init__(self):
        self.name = ''  # Inicializa a variável name

    def register(self):
        self.name = 'Banco do Brasil'  # Atribui o nome do plugin à variável self.name
    
    def get_name(self):
        return self.name
      
    def execute(self, texto):
            
        informacoes_creditos_debitos = iniciar_informacoes_creditos_debitos()

        # 1. Extrair Contrapartes de 'Principais destinatários de recursos identificados'
        padrao_contraparte = r"([\w\s]+)\s*-\s*(\d{3}\.\d{3}\.\d{3}-\d{2})\s*\(.*?\)\s*-\s*(\d+)\s+lançamento\(s\)\s+no total de:\s*R\$\s*([\d.,]+)"
        match_contraparte_secao = re.search(r"Principais destinatários de recursos identificados:\s*(.*?)(?:INFORMAÇÕES ADICIONAIS:|$)", texto, re.DOTALL | re.IGNORECASE)

        if match_contraparte_secao:
            contrapartes_secao = match_contraparte_secao.group(1)
            contrapartes = re.findall(padrao_contraparte, contrapartes_secao)
            for nome, cpf, lancamentos, valor in contrapartes:
                valor = valor.strip().replace('.', '').replace(',', '.')
                informacoes_creditos_debitos["tipo_transacao"].append("Débito")  # Assumindo que são destinatários de débitos (envios)
                informacoes_creditos_debitos["cpf"].append(cpf.strip().replace('.', '').replace('-', ''))
                informacoes_creditos_debitos["nome"].append(nome.strip())
                informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                informacoes_creditos_debitos["transacoes"].append(lancamentos.strip())
                informacoes_creditos_debitos["plataforma"].append("Não Informado")
        
        # 2. Extrair Transações PIX Recebidas
        padrao_pix_recebido = r"(\d{2}/\d{2}/\d{4})\s*-\s*R\$\s*([\d.,]+)\s*de\s*(.+?)\s*-\s*(\d{3}\.\d{3}\.\d{3}-\d{2})(?:\s*\((.*?)\))?"
        pix_recebidos_secao = re.search(r"Recebeu por meio de diversos pix.*?destacamos:(.*?)(?:Enviou recursos|Efetuou saques|$)", texto, re.DOTALL | re.IGNORECASE)
        if pix_recebidos_secao:
            pix_recebidos = pix_recebidos_secao.group(1)
            transacoes_pix = re.findall(padrao_pix_recebido, pix_recebidos)
            for data, valor, nome, cpf, profissao in transacoes_pix:
                valor = valor.strip().replace('.', '').replace(',', '.')
                informacoes_creditos_debitos["tipo_transacao"].append("Crédito")
                informacoes_creditos_debitos["cpf"].append(cpf.strip().replace('.', '').replace('-', ''))
                informacoes_creditos_debitos["nome"].append(nome.strip())
                informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                informacoes_creditos_debitos["transacoes"].append("1")  # Cada linha representa uma transação
                informacoes_creditos_debitos["plataforma"].append("Pix")

        # 3. (Opcional) Extrair Transações PIX Enviadas (se houver detalhes)
        padrao_pix_enviado = r"(\d{2}/\d{2}/\d{4})\s*-\s*R\$\s*([\d.,]+)\s*para\s*([\w\s]+)\s*-\s*(\d{3}\.\d{3}\.\d{3}-\d{2})(?:\s*\((.*?)\))?"
        pix_enviados_secao = re.search(r"Enviou recursos por meio de diversos pix.*?destacamos:(.*?)(?:Efetuou saques|$)", texto, re.DOTALL | re.IGNORECASE)
        if pix_enviados_secao:
            pix_enviados = pix_enviados_secao.group(1)
            transacoes_pix_env = re.findall(padrao_pix_enviado, pix_enviados)
            for data, valor, nome, cpf, profissao in transacoes_pix_env:
                valor = valor.strip().replace('.', '').replace(',', '.')
                informacoes_creditos_debitos["tipo_transacao"].append("Débito")
                informacoes_creditos_debitos["cpf"].append(cpf.strip().replace('.', '').replace('-', ''))
                informacoes_creditos_debitos["nome"].append(nome.strip())
                informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                informacoes_creditos_debitos["transacoes"].append("1")
                informacoes_creditos_debitos["plataforma"].append("Pix")

        if len(informacoes_creditos_debitos) > 0:
            return informacoes_creditos_debitos
        
        #
        # PROCESSA OUTRO LAYOUT DO BANCO DO BRASIL
        #
        informacoes_creditos_debitos = iniciar_informacoes_creditos_debitos()

        # 1. Extrair Contrapartes de 'Principais remetentes/depositantes identificados'
        cpf_cnpj_pattern = r"\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"
        padrao_contraparte = rf"([\w\s\.,&\-]+?)\s*-\s*({cpf_cnpj_pattern})\s*\((.*?)\)\s*-\s*(\d+)\s+lançamento\(s\)\s+no total de:\s*R\$\s*([\d.,]+)"
        match_contraparte_secao = re.search(r"Principais remetentes/depositantes identificados:\s*(.*?)(?:Resumo de lançamentos a débito|Informações complementares|$)", texto, re.DOTALL | re.IGNORECASE)

        if match_contraparte_secao:
            contrapartes_secao = match_contraparte_secao.group(1)
            contrapartes = re.findall(padrao_contraparte, contrapartes_secao)
            for nome, cpf_cnpj, descricao, lancamentos, valor in contrapartes:
                valor = valor.strip().replace('.', '').replace(',', '.')
                cpf_cnpj_clean = cpf_cnpj.strip().replace('.', '').replace('-', '').replace('/', '')
                informacoes_creditos_debitos["tipo_transacao"].append("Crédito")  # Remetentes são créditos (entradas)
                informacoes_creditos_debitos["cpf"].append(cpf_cnpj_clean)
                informacoes_creditos_debitos["nome"].append(nome.strip())
                informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                informacoes_creditos_debitos["transacoes"].append(lancamentos.strip())
                informacoes_creditos_debitos["plataforma"].append("Não Informado")
        
        # 2. Extrair Beneficiários de Cheques Emitidos
        beneficiarios_secao = re.search(r"Por amostragem, em consulta aos cheques emitidos e pagos, identificamos os seguintes beneficiários:\s*(.*?)(?:Informações complementares:|$)", texto, re.DOTALL | re.IGNORECASE)
        if beneficiarios_secao:
            beneficiarios_texto = beneficiarios_secao.group(1)
            linhas_beneficiarios = beneficiarios_texto.strip().split('\n')
            for linha in linhas_beneficiarios:
                linha = linha.strip()
                if not linha:
                    continue
                # Padrão para capturar nome, CPF/CNPJ e valor
                padrao_beneficiario = rf"([\w\s\.,&\-]+?)\s*-\s*({cpf_cnpj_pattern})(?:\s*\((.*?)\))?\s*-?\s*R\$\s*([\d.,]+)"
                match = re.match(padrao_beneficiario, linha)
                if not match:
                    # Caso especial sem hífen antes do valor
                    padrao_beneficiario = rf"([\w\s\.,&\-]+?)\s*-\s*({cpf_cnpj_pattern})(?:\s*\((.*?)\))?\s*R\$\s*([\d.,]+)"
                    match = re.match(padrao_beneficiario, linha)
                if match:
                    nome, cpf_cnpj, descricao, valor = match.groups()
                    valor = valor.strip().replace('.', '').replace(',', '.')
                    cpf_cnpj_clean = cpf_cnpj.strip().replace('.', '').replace('-', '').replace('/', '')
                    informacoes_creditos_debitos["tipo_transacao"].append("Débito")  # Beneficiários de cheques emitidos são débitos (saídas)
                    informacoes_creditos_debitos["cpf"].append(cpf_cnpj_clean)
                    informacoes_creditos_debitos["nome"].append(nome.strip())
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                    informacoes_creditos_debitos["transacoes"].append("1")  # Cada linha representa uma transação
                    informacoes_creditos_debitos["plataforma"].append("Cheque")
                else:
                    # Caso não corresponda ao padrão, tentar outro formato
                    padrao_beneficiario_alt = rf"([\w\s\.,&\-]+?)\s*-\s*({cpf_cnpj_pattern})(?:\s*\((.*?)\))?\s*([\d.,]+)"
                    match_alt = re.match(padrao_beneficiario_alt, linha)
                    if match_alt:
                        nome, cpf_cnpj, descricao, valor = match_alt.groups()
                        valor = valor.strip().replace('.', '').replace(',', '.')
                        cpf_cnpj_clean = cpf_cnpj.strip().replace('.', '').replace('-', '').replace('/', '')
                        informacoes_creditos_debitos["tipo_transacao"].append("Débito")
                        informacoes_creditos_debitos["cpf"].append(cpf_cnpj_clean)
                        informacoes_creditos_debitos["nome"].append(nome.strip())
                        informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                        informacoes_creditos_debitos["transacoes"].append("1")
                        informacoes_creditos_debitos["plataforma"].append("Cheque")
                    else:
                        # Se ainda não corresponder, pode ser um formato inesperado
                        continue

        return informacoes_creditos_debitos

