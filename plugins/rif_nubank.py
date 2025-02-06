
import re
from Lib.Functions.CriarDicionarioMovimentacoes import iniciar_informacoes_creditos_debitos, limpar_valor
from Lib.Functions.Numeros import apenas_numeros

class Plugin:
    
    def __init__(self):
        self.name = ''  # Inicializa a variável name

    def register(self):
        self.name = 'Nubank'  # Atribui o nome do plugin à variável self.name
    
    def get_name(self):
        return self.name
    
    def execute(self, texto):

        informacoes_creditos_debitos = iniciar_informacoes_creditos_debitos()

        # Expressão regular para contrapartes principais e outras contrapartes
        padrao_contraparte = r"-\s*\d{1,3},\d{2}%\s*\(R\$\s*([\d.,]+)\s*em\s*(\d+)\s*transações?\)\s*(?:via|para)\s*(CPF|CNPJ)\s*(de mesma titularidade|\d{11,14})\s*\((.*?)\)"

        # Procurar seções de Créditos e Débitos
        secoes = re.findall(r"(CRÉDITOS|DÉBITOS|OUTRAS CONTRAPARTES DE CRÉDITO|OUTRAS CONTRAPARTES DE DÉBITO):(.*?)(?=(CRÉDITOS|DÉBITOS|OUTRAS CONTRAPARTES DE CRÉDITO|OUTRAS CONTRAPARTES DE DÉBITO|Suspeitas:|$))", texto, flags=re.DOTALL)
        
        for secao_nome, secao_conteudo, _ in secoes:
            tipo_transacao = "Crédito" if "CRÉDITO" in secao_nome else "Débito"
            matches = re.findall(padrao_contraparte, secao_conteudo)
            for valor, transacoes, tipo_cadastro, cpf_cnpj, nome in matches:
                informacoes_creditos_debitos["tipo_transacao"].append(tipo_transacao)
                informacoes_creditos_debitos["cpf"].append(limpar_valor(cpf_cnpj))
                informacoes_creditos_debitos["nome"].append(nome)
                informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                informacoes_creditos_debitos["transacoes"].append(transacoes)
                informacoes_creditos_debitos["plataforma"].append("Não Informado")
    
        if len(informacoes_creditos_debitos["tipo_transacao"]) > 0:
            return informacoes_creditos_debitos
        
        #
        # PROCESSA OUTRO LAYOUT
        #
        # Extrair o CPF do titular
        cpf_titular_match = re.search(r"CPF:\s*(\d{11})", texto)
        if cpf_titular_match:
            cpf_titular = cpf_titular_match.group(1)
        else:
            cpf_titular = ""
        
        # Expressão regular para contrapartes principais
        padrao_contraparte = r"-\s*\d{1,3},\d{2}%\s*\(R\$\s*([\d.,]+)\s*em\s*(\d+)\s*transação\(ões\)\)\s*(via|para)\s*(CPF|CNPJ)\s*(de mesma titularidade|\d{11,14})\s*\((.*?)\)"
        
        # Procurar seções de Créditos e Débitos
        secoes = re.findall(r"(Total dos (créditos|débitos):\s*R\$\s*[\d.,]+.\s+-\s+Origem dos créditos|Destino dos débitos),(.*?)(?=(?:-  Total dos|Trata-se de cliente|$))", texto, flags=re.DOTALL | re.IGNORECASE)
        
        for secao_match in secoes:
            _, tipo_secao, secao_conteudo = secao_match
            tipo_transacao = "Crédito" if "crédito" in tipo_secao.lower() else "Débito"
            
            matches = re.findall(padrao_contraparte, secao_conteudo)
            for valor, transacoes, via_para, tipo_cadastro, cpf_cnpj, nome in matches:
                # Tratar CPF/CNPJ
                if cpf_cnpj == "de mesma titularidade":
                    cpf_cnpj_limpo = cpf_titular
                else:
                    cpf_cnpj_limpo = cpf_cnpj
                
                # Remover possíveis espaços e pontuações em CPF/CNPJ
                informacoes_creditos_debitos["tipo_transacao"].append(tipo_transacao)
                informacoes_creditos_debitos["cpf"].append(cpf_cnpj_limpo)
                informacoes_creditos_debitos["nome"].append(nome)
                informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                informacoes_creditos_debitos["transacoes"].append(transacoes)
                informacoes_creditos_debitos["plataforma"].append("Não Informado")

        return informacoes_creditos_debitos

