
import re
from Lib.Functions.CriarDicionarioMovimentacoes import iniciar_informacoes_creditos_debitos, limpar_valor
from Lib.Functions.Numeros import apenas_numeros

class Plugin:
    
    def __init__(self):
        self.name = ''  # Inicializa a variável name

    def register(self):
        self.name = 'Banco do Estado do Rio Grande do Sul'
    
    def get_name(self):
        return self.name
      
    def execute(self, texto):
            
        informacoes_creditos_debitos = iniciar_informacoes_creditos_debitos()

        # Padrão para encontrar as seções de créditos e débitos
        tipos_transacao = [
            ("Crédito", r"Créditos:\s*\(R\$\s*([\d,.]+)\).*?PIX no total R\$\s*([\d,.]+)(.*?)(?=Débitos|$)"),
            ("Débito", r"Débitos:\s*\(R\$\s*([\d,.]+)\).*?PIX no total R\$\s*([\d,.]+)(.*?)(?=Não foram encontradas|$)")
        ]

        # Padrão para contrapartes de transações
        padrao_contraparte = r"-\s*(.*?)\s*,\s*cuj(?:a|o)\s*atividade\s*é\s*(.*?)\s*,\s*(?:residente em|com sede em)\s*(.*?)\(\d+\s*transações?\s*que\s*somam\s*R\$\s*([\d,.]+)\)"

        for tipo, padrao_secao in tipos_transacao:
            match_secao = re.search(padrao_secao, texto, re.DOTALL)
            if match_secao:
                valor_total = match_secao.group(1)  # Valor total da transação
                secao_contrapartes = match_secao.group(3)  # Texto com contrapartes

                # Extrair informações das contrapartes na seção
                contrapartes = re.findall(padrao_contraparte, secao_contrapartes)

                for match in contrapartes:
                    nome, atividade, localidade, valor = match
                    informacoes_creditos_debitos["tipo_transacao"].append(tipo)
                    informacoes_creditos_debitos["cpf"].append('')  # CPF não está disponível no texto
                    informacoes_creditos_debitos["nome"].append(nome.strip())
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                    informacoes_creditos_debitos["transacoes"].append('')  # Quantidade de transações não extraída
                    informacoes_creditos_debitos["plataforma"].append("PIX")

        return informacoes_creditos_debitos

