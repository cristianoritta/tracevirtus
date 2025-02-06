
import re
from Lib.Functions.CriarDicionarioMovimentacoes import iniciar_informacoes_creditos_debitos, limpar_valor
from Lib.Functions.Numeros import apenas_numeros

class Plugin:
    
    def __init__(self):
        self.name = ''  # Inicializa a variável name

    def register(self):
        self.name = 'Caixa Econômica Federal'  # Atribui o nome do plugin à variável self.name
    
    def get_name(self):
        return self.name
      
    def execute(self, texto):
            
        informacoes_creditos_debitos = iniciar_informacoes_creditos_debitos()

        # Padrões para seções de créditos e débitos
        padroes = [
            ("Crédito", r"Os principais créditos foram:.*?:\s*(.*?)(?=DESTINO DOS RECURSOS|CARACTERÍSTICAS|$)", "CRED"),
            ("Débito", r"Os principais débitos foram:.*?:\s*(.*?)(?=CARACTERÍSTICAS|INFORMAÇÕES ADICIONAIS|$)", "DEB")
        ]

        # Padrão para contrapartes com CPF/CNPJ
        padrao_contraparte = r"R\$ ([\d.,]+)\s*-\s*(.*?),\s*(?:CPF|CNPJ)?\s*([\d./-]+)?"

        # Padrão para saques/depósitos com múltiplas datas
        padrao_fragmentado = r"(\d{2}/\d{2}/\d{4})\s*-\s*R\$\s*([\d.,]+)"

        for tipo, padrao_secao, tipo_abrev in padroes:
            match_secao = re.search(padrao_secao, texto, re.DOTALL)
            if match_secao:
                secao = match_secao.group(1)

                # Capturar saques/depósitos com datas separadamente
                fragmentados = re.findall(padrao_fragmentado, secao)
                for data, valor in fragmentados:
                    informacoes_creditos_debitos["tipo_transacao"].append(tipo)
                    informacoes_creditos_debitos["cpf"].append("")  # Sem CPF em saques/depósitos
                    informacoes_creditos_debitos["nome"].append(f"Saque/Depósito em {data}")
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                    informacoes_creditos_debitos["transacoes"].append(f"{tipo_abrev}")
                    informacoes_creditos_debitos["plataforma"].append("OUTRO")

                # Extrair outras transações com nome e CPF/CNPJ
                contrapartes = re.findall(padrao_contraparte, secao)
                for valor, nome, id_doc in contrapartes:
                    if re.match(r"\d{2}/\d{2}/\d{4}", nome):  # Ignorar nomes que são datas
                        continue
                    informacoes_creditos_debitos["tipo_transacao"].append(tipo)
                    informacoes_creditos_debitos["cpf"].append(apenas_numeros(id_doc.strip()) if id_doc else "")
                    informacoes_creditos_debitos["nome"].append(nome.strip() if nome else "Transação sem nome")
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor.strip()))
                    informacoes_creditos_debitos["transacoes"].append(f"{tipo_abrev}")
                    informacoes_creditos_debitos["plataforma"].append("PIX" if "PIX" in nome.upper() else "OUTRO")

        return informacoes_creditos_debitos