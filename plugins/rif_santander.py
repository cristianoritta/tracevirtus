
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
    
    def extrair_transacoes(self, texto, tipo):
        """
        Função genérica para extrair transações de crédito e débito.
        """
        informacoes = iniciar_informacoes_creditos_debitos()

        padrao_transacoes = re.compile(
            r"R\$\s?([\d,.]+)\s+em\s+(\d+)\s+(\w+)[s]?\s+sendo.*?principais\s+(\w+):\s+"
            r"(?:o\s+R\$\s?([\d,.]+)\s+([\w\s&-]+)\s+(CNPJ|CPF)[:]\s?(\d{11,14}).*?)+",
            re.DOTALL
        )

        for match in padrao_transacoes.finditer(texto):
            valor_total = limpar_valor(match.group(1))
            transacoes = int(match.group(2))
            plataforma = match.group(3).upper()

            # Captura múltiplos beneficiários/ordenantes
            matches_individuais = re.findall(
                r"o\s+R\$\s?([\d,.]+)\s+([\w\s&-]+)\s+(CNPJ|CPF)[:]\s?(\d{11,14})", match.group(0)
            )

            for transacao in matches_individuais:
                valor = limpar_valor(transacao[0])
                nome = transacao[1].strip().replace('- ', '')
                documento = transacao[3]

                informacoes["tipo_transacao"].append(tipo)
                informacoes["cpf"].append(documento)
                informacoes["nome"].append(nome)
                informacoes["valor"].append(valor)
                informacoes["transacoes"].append(transacoes)
                informacoes["plataforma"].append(plataforma)

        return informacoes
      
    def execute(self, texto):
            
        informacoes_creditos_debitos = iniciar_informacoes_creditos_debitos()

        # Regex para identificar remetentes e valores recebidos
        padrao_remetentes = re.compile(
            r"(?P<nome>[\w\s&-]+) - CNPJ: (?P<cpf_cnpj>\d{14}) - Valor Recebido: R\$(?P<valor>[\d,.]+) , sendo: (?P<detalhes>.+?)\s{2}",
            re.DOTALL
        )

        # Regex para identificar destinatários e valores enviados
        padrao_destinatarios = re.compile(
            r"(?P<nome>[\w\s&-]+) - (CNPJ|CPF): (?P<cpf_cnpj>\d{11,14}) - Valor Enviado: R\$(?P<valor>[\d,.]+) , sendo: (?P<detalhes>.+?)\s{2}",
            re.DOTALL
        )

        # Processar remetentes
        for match in padrao_remetentes.finditer(texto):
            detalhes = match.group("detalhes")
            transacoes = sum(int(num) for num, _ in re.findall(r"(\d+) (PIX|TED|RESGATES)", detalhes))

            informacoes_creditos_debitos["tipo_transacao"].append("Crédito")
            informacoes_creditos_debitos["cpf"].append(match.group("cpf_cnpj"))
            informacoes_creditos_debitos["nome"].append(match.group("nome").strip().replace('- ',''))
            informacoes_creditos_debitos["valor"].append(limpar_valor(match.group("valor")))
            informacoes_creditos_debitos["transacoes"].append(transacoes)
            informacoes_creditos_debitos["plataforma"].append("PIX/TED")

        # Processar destinatários
        for match in padrao_destinatarios.finditer(texto):
            detalhes = match.group("detalhes")
            transacoes = sum(int(num) for num, _ in re.findall(r"(\d+) (PIX|TED)", detalhes))

            informacoes_creditos_debitos["tipo_transacao"].append("Débito")
            informacoes_creditos_debitos["cpf"].append(match.group("cpf_cnpj"))
            informacoes_creditos_debitos["nome"].append(match.group("nome").strip().replace('- ',''))
            informacoes_creditos_debitos["valor"].append(limpar_valor(match.group("valor")))
            informacoes_creditos_debitos["transacoes"].append(transacoes)
            informacoes_creditos_debitos["plataforma"].append("PIX/TED")

        if len(informacoes_creditos_debitos["tipo_transacao"]) > 0:
            return informacoes_creditos_debitos


        # METODO 2
        #####################
        informacoes_creditos = self.extrair_transacoes(texto, "Crédito")
        informacoes_debitos = self.extrair_transacoes(texto, "Débito")

        # Combina os dicionários resultantes
        for chave in informacoes_creditos.keys():
            informacoes_creditos[chave].extend(informacoes_debitos[chave])

        return informacoes_creditos
        













