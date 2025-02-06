
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

        # Padrão para contrapartes
        padrao_contraparte = r"R\$\s*([\d,.]+)\s*-\s*(\d+)\s*transações?\s*-\s*(.*?)\s*-\s*(\d{11,14})\s*-\s*(.*?)(?=\s*R\$|\s*$)"

        # Lista de tipos de transação a serem processados
        tipos_transacao = [
            ("Crédito", r"Os créditos ocorreram por meio de:(.*?)(?:Destino dos Recursos:|Os débitos ocorreram por meio de:)"),
            ("Débito", r"Os débitos ocorreram por meio de:(.*?)(?:Enquadramento dos Riscos|$)")
        ]

        for tipo, padrao_secao in tipos_transacao:
            match_secao = re.search(padrao_secao, texto, re.DOTALL)
            if match_secao:
                secao = match_secao.group(1)

                # Extrair métodos de transação e valores (se necessário)
                methods = re.findall(r"\s*(.*?):\s*R\$\s*([\d,.]+)\s*-\s*(\d+)\s*transações?", secao)

                # Extrair contrapartes
                contrapartes_match = re.search(r"Em amostra identificamos as principais contrapartes:\s*(.*?)(?:\n\n|\n\s*\w+:|$)", secao, re.DOTALL)
                if contrapartes_match:
                    contrapartes = contrapartes_match.group(1)

                    # Encontrar todas as contrapartes
                    for match in re.findall(padrao_contraparte, contrapartes):
                        valor, transacoes, nome, cpf, plataforma = match
                        informacoes_creditos_debitos["tipo_transacao"].append(tipo)
                        informacoes_creditos_debitos["cpf"].append(apenas_numeros(cpf.strip()))
                        informacoes_creditos_debitos["nome"].append(nome.strip())
                        informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                        informacoes_creditos_debitos["transacoes"].append(transacoes.strip())
                        informacoes_creditos_debitos["plataforma"].append(plataforma.strip())

        if len(informacoes_creditos_debitos) > 0:
            informacoes_creditos_debitos

        #
        # PROCESSA OUTRO LAYOUT DO BANCO DO BRASIL
        #

        # 1. Extrair transações de Entrada
        padrao_entrada = r"Entrada:\s*(.*?)\s*(?=Saída:|$)"
        entrada_match = re.search(padrao_entrada, texto, re.DOTALL)
        if entrada_match:
            entrada_texto = entrada_match.group(1)
            padrao_transacao = r"(\d{2}/\d{2}/\d{4}\s*\d{2}:\d{2})\s+(.*?)\s+(\d{11,14})\s+R\$\s*([\d.,]+)"
            transacoes = re.findall(padrao_transacao, entrada_texto)
            for data, nome, cpf, valor in transacoes:
                if valor != '':
                    informacoes_creditos_debitos["tipo_transacao"].append("Crédito")
                    informacoes_creditos_debitos["cpf"].append(apenas_numeros(cpf.strip()))
                    informacoes_creditos_debitos["nome"].append(nome.strip())
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                    informacoes_creditos_debitos["transacoes"].append("1")
                    informacoes_creditos_debitos["plataforma"].append("Não Informado")

        # 2. Extrair transações de Saída
        padrao_saida = r"Saída:\s*(.*?)\s*(?=Chama atenção|$)"
        saida_match = re.search(padrao_saida, texto, re.DOTALL)
        if saida_match:
            saida_texto = saida_match.group(1)
            padrao_transacao = r"(\d{2}/\d{2}/\d{4}\s*\d{2}:\d{2})\s+(.*?)\s+(\d{11,14})\s+R\$\s*([\d.,]+)"
            transacoes = re.findall(padrao_transacao, saida_texto)
            for data, nome, cpf, valor in transacoes:
                if valor != '':
                    informacoes_creditos_debitos["tipo_transacao"].append("Débito")
                    informacoes_creditos_debitos["cpf"].append(apenas_numeros(cpf.strip()))
                    informacoes_creditos_debitos["nome"].append(nome.strip())
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                    informacoes_creditos_debitos["transacoes"].append("1")
                    informacoes_creditos_debitos["plataforma"].append("Não Informado")

        # 3. Extrair principais emitentes (Origem dos Recursos)
        padrao_origem = r"ORIGEM DOS RECURSOS:.*?principal\(ais\) emitentes\(s\):\s*(.*?)(?=DESTINO DOS RECURSOS:|ENQUADRAMENTO DOS RISCOS|$)"
        origem_match = re.search(padrao_origem, texto, re.DOTALL)
        if origem_match:
            origem_texto = origem_match.group(1)
            padrao_contraparte = r"(.*?),\s*(\d{11,14})\s*\[.*?\]\s*\(R\$\s*([\d.,]+)\)\s*Quantidade de transações:\s*(\d+)"
            contrapartes = re.findall(padrao_contraparte, origem_texto)
            for nome, cpf, valor, transacoes in contrapartes:
                if valor != '':
                    informacoes_creditos_debitos["tipo_transacao"].append("Crédito")
                    informacoes_creditos_debitos["cpf"].append(apenas_numeros(cpf.strip()))
                    informacoes_creditos_debitos["nome"].append(nome.strip())
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                    informacoes_creditos_debitos["transacoes"].append(transacoes.strip())
                    informacoes_creditos_debitos["plataforma"].append("PIX")

        # 4. Extrair principais favorecidos (Destino dos Recursos)
        padrao_destino = r"DESTINO DOS RECURSOS:.*?principal\(ais\) favorecidos\(s\):\s*(.*?)(?=A diferença de valores|ENQUADRAMENTO DOS RISCOS|$)"
        destino_match = re.search(padrao_destino, texto, re.DOTALL)
        if destino_match:
            destino_texto = destino_match.group(1)
            padrao_contraparte = r"(.*?),\s*(\d{11,14})\s*\[.*?\]\s*\(R\$\s*([\d.,]+)\)\s*Quantidade de transações:\s*(\d+)"
            contrapartes = re.findall(padrao_contraparte, destino_texto)
            for nome, cpf, valor, transacoes in contrapartes:
                if valor != '':
                    informacoes_creditos_debitos["tipo_transacao"].append("Débito")
                    informacoes_creditos_debitos["cpf"].append(apenas_numeros(cpf.strip()))
                    informacoes_creditos_debitos["nome"].append(nome.strip())
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                    informacoes_creditos_debitos["transacoes"].append(transacoes.strip())
                    informacoes_creditos_debitos["plataforma"].append("PIX")

        if len(informacoes_creditos_debitos) > 0:
            return informacoes_creditos_debitos

        #
        # PROCESSA OUTRO LAYOUT DO BANCO DO BRASIL
        #        
        
        # Padrões para identificar as seções de créditos e débitos totais
        tipos_transacao = [
            ("Crédito", r"ORIGEM DOS RECURSOS:.*?CRÉDITOR\$\s*([\d,.]+).*?PIX ENTRADA\s*([\d,.]+).*?(?=DESTINO DOS RECURSOS|ENQUADRAMENTO DOS RISCOS)"),
            ("Débito", r"DESTINO DOS RECURSOS:.*?DÉBITO\s*R\$\s*([\d,.]+).*?PIX SAIDA\s*([\d,.]+).*?(?=ENQUADRAMENTO DOS RISCOS|$)")
        ]
        
        # Padrões específicos para capturar contrapartes de crédito e débito
        padrao_contraparte_entrada = r"([A-Z\s]+?)\s+(\d{11,14})\s+PIX ENTRADA.*?R\$\s*([\d,.]+)"
        padrao_contraparte_saida = r"([A-Z\s]+?)\s+(\d{11,14}(?:\s+\d{14})?)\s+PIX SAIDA.*?R\$\s*([\d,.]+)"

        # Extrair informações para cada tipo de transação
        for tipo, padrao_secao in tipos_transacao:
            match_secao = re.search(padrao_secao, texto, re.DOTALL)
            
            # Verificação da seção de crédito ou débito
            if match_secao:
                # Identificar contrapartes com base no tipo de transação
                if tipo == "Crédito":
                    contrapartes = re.findall(padrao_contraparte_entrada, match_secao.group(0))
                else:
                    contrapartes = re.findall(padrao_contraparte_saida, match_secao.group(0))

                # Processar cada contraparte encontrada
                for match in contrapartes:
                    nome, cpf, valor = match
                    informacoes_creditos_debitos["tipo_transacao"].append(tipo)
                    informacoes_creditos_debitos["cpf"].append(cpf.strip())
                    informacoes_creditos_debitos["nome"].append(nome.strip())
                    informacoes_creditos_debitos["valor"].append(limpar_valor(valor))
                    informacoes_creditos_debitos["transacoes"].append("")  # Número de transações não identificado
                    informacoes_creditos_debitos["plataforma"].append("PIX")

        return informacoes_creditos_debitos














