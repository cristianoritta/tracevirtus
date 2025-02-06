# Bibliotecas padrão
import importlib
import json
import os
import time
import markdown
import Lib.Controller.CasoController as CasoController
import Lib.Controller.SimbaController as SimbaController
import Lib.Controller.CooperacaoController as CooperacaoController
import Lib.Controller.RifController as RifController
import Lib.Controller.RelatorioController as RelatorioController
import Lib.Controller.AtualizacaoController as AtualizacaoController
import Lib.Controller.PessoaController as PessoaController
import Lib.Controller.IaController as IaController
import Lib.Database as Database


# Bibliotecas de terceiros
from flask import (
    jsonify, render_template, request, session, redirect,
    send_from_directory, get_flashed_messages, flash, send_file
)
from docx import Document

# Bibliotecas locais (projeto específico)
import Lib.Log
from Lib.Functions.PrintColor import printcolor
from Lib.Controller.ConfiguracaoController import APPPATH
from __main__ import app

# Middleware
import Lib.Middleware.Auth as Auth
import Lib.Middleware.Version as Version
import Lib.Middleware.Upload as Upload

# Controllers
import Lib.Controller.HomeController as HomeController
import Lib.Controller.ConfiguracaoController as ConfiguracaoController

Logger = Lib.Log.logger

@app.before_request
def hook():
    ###################
    #  Rotas protegidas
    ###################
    routes_version = {'home', 'casos'}
    routes_auth = routes_version

    get_flashed_messages()

    # Rotas protegidas por controle de versão
    if request.endpoint in routes_version:
        if Version.checkVersion() != True:
            return redirect('/update')

    # Rotas protegidas por autenticação do usuário
    if request.endpoint in routes_auth:
        #status_token = Auth.checkToken()
        status_token = True

        # TODO: Revisar aqui
        if status_token == 'expired':
            return redirect('/assinatura')
        elif status_token != True:
            return redirect('/minhaconta')


#####################
#   MAIN ROUTE
#####################
@app.route("/")
@app.route("/home")
def home():
    return HomeController.index()


#####################
#   RENDER FILTERS
#####################
@app.template_filter(name='linebreaksbr')
def linebreaksbr_filter(text):
    if text == None:
        return ''

    return text.replace('\n', '<br>')


@app.template_filter(name='len')
def len_filter(ar):
    return len(ar)


#####################
#   MINHA CONTA
#####################
@app.route("/minhaconta", methods=['POST', 'GET'])
def minhaconta():

    if request.method == 'POST':
        Auth.save(request.form)
        ConfiguracaoController.save(request)

    usuario = Auth.get_user()
    configuracoes = ConfiguracaoController.get_configuracoes()
    versao = Version.getVersion()

    return render_template("minhaconta.html", usuario=usuario, versao=versao, configuracoes=configuracoes)


#####################
#   CASOS
#####################
@app.route("/casos")
def casos():
    casos = CasoController.get_casos()

    return render_template("casos/index.html", casos=casos)

@app.route("/casos/form/", defaults={'id': None})
@app.route("/casos/form/<int:id>")
def form(id):

    if request.method == 'POST':
        id = CasoController.save(request)
        return redirect('/casos')

    if id:
        id = CasoController.find(id)
    
    return render_template("casos/form.html", caso=id)

@app.route("/casos/store/", methods=['POST'])
def store():
    if request.method == 'POST':
        id = CasoController.save(request)
        return redirect('/casos')

@app.route("/casos/ativo/<int:id>")
def set_ativo(id):
    message = CasoController.set_ativo(id)
    
    return message


@app.route("/casos/excluir/<int:id>")
def caso_excluir(id):
    
    message = CasoController.excluir(id)
    
    return message


@app.route("/casos/chat", methods=['POST', 'GET'])
def caso_chat():
    
    dialogos = ""#dialogos = CasoController.chat_contexto(request)
    
    return render_template('casos/chat.html', dialogos=dialogos)



###########################
#   PESSOAS E INVESTIGADOS
###########################
@app.route("/investigados", defaults={'caso_id': None})
@app.route("/investigados/<caso_id>")
def investigados(caso_id):

    if caso_id:
        caso = CasoController.find(caso_id)

        # A partir de agora, esse é o caso ativo
        CasoController.set_ativo(caso_id)
    else:
        caso = CasoController.get_ativo()
    
    if not caso:
        flash("warning: Você precisa definir um caso ativo.")
        return redirect('/casos')

    investigados = PessoaController.get_investigados(caso.id)

    return render_template("pessoas/investigados.html", 
                           caso=caso, 
                           investigados=investigados, 
                        )

@app.route("/pessoas/modal/investigado")
def pessoas_modal_investigado():
    return render_template("pessoas/modal/investigado.html")


@app.route("/pessoas/store/investigado", methods=['POST'])
def pessoas_investigado_store():

    PessoaController.save_investigado(request)

    return redirect('/investigados')


@app.route("/pessoa/cpf/<int:cpf>")
def get_pessoa_por_cpf(cpf):
    
    pessoa = PessoaController.cpf(cpf)

    return render_template("pessoas/pessoa.html", pessoa=pessoa)


#####################
#   COAF / RIF
#####################
@app.route("/rif", defaults={'caso_id': None})
@app.route("/rif/<int:caso_id>")
def rif(caso_id):
    
    if caso_id:
        caso = CasoController.find(caso_id)

        # A partir de agora, esse é o caso ativo
        CasoController.set_ativo(caso_id)
    else:
        caso = CasoController.get_ativo()
    
    if not caso:
        flash("warning: Você precisa definir um caso ativo.")
        return redirect('/casos')

    rifs = []
    for rif in RifController.get_rifs(caso.id):
        rifs.append({
            'id': rif[0],
            'numero': rif[2],
            'instituicoes': Database.query(f"SELECT * FROM comunicacoes WHERE caso_id = {caso.id} and rif_id = {rif[0]} GROUP BY cpfCnpjComunicante"),
            'titulares': RifController.get_titulares(rif[0]),
            'arquivos': RifController.get_arquivos(rif[0])
        })
    
    # TODO: Retirar daqui e colocar na RifController
    
    arquivos = Database.query(f"SELECT * FROM arquivos WHERE caso_id = {caso.id} AND tipo = 'rifs'")
    titulares = Database.query(f"SELECT * FROM envolvidos WHERE caso_id = {caso.id} AND tipoEnvolvido = 'Titular'")    

    return render_template("rif/index.html", 
                           caso=caso, 
                           rifs = rifs, 
                        )

@app.route("/rif/modal/novo")
def rif_modal_novo():
    return render_template("rif/modal/novo.html")


@app.route("/rif/modal/store/", methods=['POST'])
def rif_modal_store():

    RifController.save(request)

    return redirect('/rif')


@app.route("/rif/modal/upload/<int:id>")
def rif_modal_upload(id):
    return render_template("rif/modal/upload.html", rif=id)

@app.route("/rif/modal/comunicacao/<int:rif_id>/<int:indexador>/<int:informacao_id>")
def rif_modal_comunicacao(rif_id, indexador, informacao_id):
    
    informacoes_adicionais = RifController.get_informacoes_adicionais(informacao_id)

    comunicacao = RifController.get_comunicacao(rif_id, indexador)

    # TODO Salvar essa analise no banco de dados para não precisar carregar novamente.
    # Pode ser uma analise para cada (nome+Indexador = mais economico) ou uma para cada informacoes_adicionais.id
    analise = IaController.executar_ia([{'role': 'user', 'content': f"Faça uma análise de contexto no <texto>, para encontrar o que há de informações sobre <nomeEnvolvido>. <texto>{comunicacao['informacoesAdicionais']}</texto> <nomeEnvolvido>{informacoes_adicionais['nome']}</nomeEnvolvido>"}])

    return render_template("rif/modal/comunicacao.html", comunicacao=comunicacao, analise=analise)




@app.route("/rif/upload/", methods=['GET','POST'])
def rif_upload():

    if request.method == 'POST':
        resultado = RifController.upload(request)

    return render_template("rif/concluido.html", resultado=resultado, rif=request.form.get('rif_id'))


@app.route("/rif/naoprocessadas/<int:id>")
def rif_naoprocessadas(id):

    caso = CasoController.get_ativo()
    rif = Database.find(Database.rifs, id)

    rif_naoprocessadas = RifController.get_naoprocessadas(rif.id)

    return render_template("rif/naoprocessadas.html", caso=caso, rif=rif, naoprocessadas=rif_naoprocessadas)




@app.route("/rif/arquivos/<int:id>")
def rif_arquivos(id):

    caso = CasoController.get_ativo()
    rif = RifController.find(id)
    arquivos = RifController.get_arquivos(id)

    return render_template("rif/arquivos.html", caso=caso, rif=rif, arquivos=arquivos)


@app.route("/rif/instituicoes/<int:id>")
def rif_instituicoes(id):

    caso = CasoController.get_ativo()
    rif = RifController.find(id)
    instituicoes = RifController.get_instituicoes(id)

    return render_template("rif/instituicoes.html", caso=caso, rif=rif, instituicoes=instituicoes)

@app.route("/rif/modal/instituicoes/<int:rif_id>")
@app.route("/rif/modal/instituicoes/<int:rif_id>/<int:id>")
def rif_modal_instituicoes(rif_id, id = None):
    
    rif = RifController.find(rif_id)

    if id:
        informacao_adicional = Database.engine.connect().execute(Database.informacoes_adicionais.select().where(Database.informacoes_adicionais.c.id == id)).fetchone()
    else:
        informacao_adicional = None        

    return render_template("rif/modal/informacoes_adicionais.html", rif=rif, informacao_adicional=informacao_adicional)

@app.route("/rif/modal/instituicoes/store/",  methods=['POST'])
def rif_modal_instituicoes_store():

    rif_id = request.form.get('rif_id')

    RifController.save_informacoes_adicionais(request)

    return redirect(f'/rif/instituicoes/{rif_id}')



@app.route("/rif/titulares/<int:id>")
def rif_titulares(id):

    rif = RifController.find(id)

    envolvidos = RifController.get_envolvidos(id)
    investigados = PessoaController.get_investigados(rif.caso_id)

    # Cria um conjunto de CPFs (ou IDs) dos investigados para facilitar a busca
    cpfs_investigados = {int(investigado['cpf_cnpj']) for investigado in investigados}

    # Adiciona a coluna 'investigado' na lista de envolvidos
    for envolvido in envolvidos:
        envolvido['investigado'] = int(envolvido['cpfCnpjEnvolvido']) in cpfs_investigados
    

    return render_template("rif/envolvidos.html", 
                           caso=CasoController.get_ativo(), 
                           rif=RifController.find(id), 
                           envolvidos=envolvidos,
                           investigados=investigados,
                           )


@app.route("/rif/excluir/<int:id>", methods=['DELETE'])
def excluir_rif(id):

    mensagem, status = RifController.excluir(id)
    
    # TODO Não está removendo automaticamente no front-end
    return jsonify({"message": mensagem}), status


@app.route("/rif/chat/", methods=['GET','POST'])
def rif_chat():

    chat = []

    if request.method == 'POST':
        chat = IaController.chat(request)

    return render_template("rif/chat.html", dialogos = chat)


@app.route("/rif/exportar/")
def rif_exportar():

    return RifController.exportar()


@app.route("/rif/relatorio/")
def rif_relatorio():

    RelatorioController.rif()

    return redirect('/rif')




#####################
#   SIMBA
#####################
@app.route("/simba", defaults={'caso_id': None})
@app.route("/simba/<int:caso_id>")
def simba(caso_id):

    if caso_id:
        caso = CasoController.find(caso_id)

        # A partir de agora, esse é o caso ativo
        CasoController.set_ativo(caso_id)
    else:
        caso = CasoController.get_ativo()

    if not caso:
        flash("warning: Você precisa definir um caso ativo.")
        return redirect('/casos')

    cooperacoes = CooperacaoController.get_cooperacoes(CasoController.get_ativo().id)
    dados = CooperacaoController.get_cooperacoes_dados(CasoController.get_ativo().id)

    return render_template("simba/index.html", caso=caso, cooperacoes=cooperacoes, dados = dados)

@app.route("/simba/modal/cooperacao")
def simba_modal_cooperacao():
    return render_template("simba/modal/cooperacao.html")


@app.route("/simba/cooperacao/store/", methods=['POST'])
def simba_cooperacao_store():

    CooperacaoController.save(request)

    return redirect('/simba')

@app.route("/simba/excluir/cooperacao/<int:id>", methods=['DELETE'])
def excluir_cooperacao(id):

    mensagem, status = CooperacaoController.excluir(id)
    
    # TODO Não está removendo automaticamente no front-end
    return jsonify({"message": mensagem}), status

@app.route("/simba/modal/upload/<int:id>")
def simba_modal_upload(id):
    return render_template("simba/modal/upload.html", cooperacao=id)


@app.route("/simba/upload/", methods=['GET', 'POST'])
def simba_upload():

    arquivos = 0
    registros = 0

    if request.method == 'POST':
        arquivos, registros = SimbaController.upload(request)

        # Testa as atualizações do banco de dados
        AtualizacaoController.atualizar('bancos')
    
    return render_template("simba/concluido.html", arquivos=arquivos, registros=registros)


@app.route("/simba/unificar/nomes")
def simba_unificar_nomes():

    # Lista todos os alvos do Caso ativo
    pessoas_unificar = SimbaController.unificar_nomes()

    # Processa os dados com IA para sugerir uma unificação a partir do nome/cpf
    analise_ia = IaController.unificardados(pessoas_unificar)

    return render_template("simba/unificar.html", 
                           pessoas = SimbaController.unificar_nomes(), 
                           caso = CasoController.get_ativo(),
                           analise_ia = markdown.markdown(analise_ia)
                        )

@app.route("/simba/unificar/nomes/corrigir", methods=['POST'])
def simba_corrigir_nomes():

    # Lista todos os alvos do Caso ativo
    try:
        SimbaController.corrigir_nomes(request)
        flash('success:Nomes unificados com sucesso.')
    except:
        flash('danger:Erro ao unificar nomes.')

    return redirect('/simba/unificar/nomes')


@app.route("/simba/unificar/cpfs")
def simba_unificar_cpfs():

    try:
        SimbaController.corrigir_cpfs()
        flash('success:CPFs unificados com sucesso.')
    except Exception as e:
        printcolor.danger(e)
        flash('danger:Erro ao unificar CPFs.')
    
    return redirect('/simba')


@app.route("/simba/arquivos/<int:id>")
def simba_arquivos(id):

    caso = CasoController.get_ativo()
    cooperacao = CooperacaoController.find(id)
    arquivos = CooperacaoController.get_cooperacoes_dados(caso.id)

    return render_template("simba/arquivos.html", caso=caso, cooperacao=cooperacao, arquivos=arquivos[id]['arquivos'])

@app.route("/simba/arquivos/<int:id>/excluir", methods=['DELETE'])
def excluir_arquivo_simba(id):

    mensagem, status = SimbaController.excluir_arquivo(id)
    
    # TODO Não está removendo automaticamente no front-end
    return jsonify({"message": mensagem}), status


@app.route("/simba/bancos/<int:id>")
def simba_bancos(id):

    caso = CasoController.get_ativo()
    cooperacao = CooperacaoController.find(id)
    bancos = CooperacaoController.get_bancos(id)

    return render_template("simba/bancos.html", caso=caso, cooperacao=cooperacao, bancos=bancos)

@app.route("/simba/relatorio")
def simba_relatorio():

    RelatorioController.simba()

    return "Relatorio gerado com sucesso"
    

#####################
#       IA
#####################
@app.route("/ia")
def ia_llm():
    llm = Database.find(Database.llms, 1)
    print(llm)
    return render_template('/ia/llm.html', llm = llm)

@app.route("/ia/llm/store", methods=['POST'])
def llm_store():
    return IaController.llm_store(request)

@app.route("/chat")
def chat():
    return redirect('/rif/chat')



#####################
#   PLUGINS
#####################
@app.route("/plugins", methods=['POST', 'GET'])
def plugins():

    if request.method == 'POST':
        Auth.save(request.form)
        ConfiguracaoController.save(request)

    plugins = PluginController.get_plugins()

    return render_template("plugins/plugins.html")


#####################
#   ATUALIZAÇÕES
#####################
@app.route("/atualizacoes")
def atualizacoes():
    return render_template('/atualizacoes/index.html')

@app.route("/atualizacoes/<bancodedados>")
def atualizacoes_bancodedados(bancodedados):

    AtualizacaoController.atualizar(bancodedados)

    return redirect('/atualizacoes')


#####################
#   TREINAMENTOS
#####################
@app.route("/treinamentos")
def treinamentos():

    return render_template("treinamentos/index.html")