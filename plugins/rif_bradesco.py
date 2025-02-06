
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
        result = {
            "tipo_transacao": [],
            "cpf": [],
            "nome": [],
            "valor": [],
            "transacoes": [],
            "plataforma": []
        }

        # Pattern for PIX transactions
        pix_pattern = r'((?:Crédito|Débito))\s+([A-Za-zÀ-ú\s\.]+)\s+(\d{9}[-\d]*|\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})\s+([\d\.,]+)'
        
        # Updated pattern for main credits (remetentes)
        credit_pattern = r'([\d\.,]+)\s+(\d+)\s+([A-Za-zÀ-ú\s&]+?(?:Ltda|Eireli)?)\s+(\d{9}[-\d]*|\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})\s+([A-Za-z\s\/]+(?:\/\s*[A-Za-z]+)*)'
        
        # Pattern for main debits (favorecidos)
        debit_pattern = r'([\d\.,]+)\s+(\d+)\s+([A-Za-zÀ-ú\s&]+?(?:Ltda|Eireli)?)\s+(\d{9}[-\d]*|\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})\s+([A-Za-z\s\/\(\)\d]+(?:\/\s*[A-Za-z]+)*)'
        
        # Find PIX transactions
        for match in re.finditer(pix_pattern, texto):
            tipo = match.group(1)
            nome = match.group(2).strip()
            documento = match.group(3)
            valor = match.group(4)
            
            result["tipo_transacao"].append(tipo)
            result["nome"].append(nome)
            result["cpf"].append(documento)
            result["valor"].append(limpar_valor(valor))
            result["transacoes"].append(1)
            result["plataforma"].append("PIX")
        
        # Find main credits
        remetentes_section = re.search(r'principais remetentes:.*?(?=Os débitos|$)', texto, re.DOTALL)
        if remetentes_section:
            remetentes_text = remetentes_section.group(0)
            # Print for debugging
            for match in re.finditer(credit_pattern, remetentes_text):
                valor = match.group(1)
                qtde = match.group(2)
                nome = match.group(3).strip()
                documento = match.group(4)
                banco = match.group(5).strip()
                
                result["tipo_transacao"].append("Crédito")
                result["nome"].append(nome)
                result["cpf"].append(documento)
                result["valor"].append(limpar_valor(valor))
                result["transacoes"].append(int(qtde))
                result["plataforma"].append(banco)
        
        # Find main debits
        favorecidos_section = re.search(r'principais favorecidos:.*?(?=Notas:|$)', texto, re.DOTALL)
        if favorecidos_section:
            for match in re.finditer(debit_pattern, favorecidos_section.group(0)):
                valor = match.group(1)
                qtde = match.group(2)
                nome = match.group(3).strip()
                documento = match.group(4)
                banco = match.group(5).strip()
                
                result["tipo_transacao"].append("Débito")
                result["nome"].append(nome)
                result["cpf"].append(documento)
                result["valor"].append(limpar_valor(valor))
                result["transacoes"].append(int(qtde))
                result["plataforma"].append(banco)
        

        print(result)

        return result