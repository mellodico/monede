from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.forms import UserCreationForm
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import render, redirect,  get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from .models import Transacao, Categoria, DespesaPlanejada, Pagamento, Meta, Limites , Subcategoria, Cartao, Conta, Banco, Logo
from .forms import TransacaoForm, PagamentoForm, CategoriaForm, SubcategoriaForm, CartaoForm, TransacaoCartaoForm, ContaForm, BancoForm
from .calculations import FinancialAnalyzer
import json
import joblib
import requests
from datetime import datetime, timedelta


modelo_ml = joblib.load('ml_model.pkl')


def registrar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registrar.html', {'form': form})


def inicio_view(request):
    transacoes = Transacao.objects.order_by('-data')[:5]
    return render(request, 'financas/inicio.html', {'transacoes': transacoes})


def obter_logo_via_api(marca_nome):
    """
    Tenta obter o logo de uma marca utilizando múltiplas fontes.
    """
    fontes = [buscar_logo_brandfetch, buscar_logo_clearbit]  
    
    for fonte in fontes:
        logo = fonte(marca_nome)  # Tenta buscar o logo com cada fonte
        if logo:  # Se encontrar um logo, retorna
            return logo
    
    # Retorna logo padrão se nenhuma fonte encontrar
    print(f"Logo não encontrado para {marca_nome}. Usando logo padrão.")
    logo, _ = Logo.objects.get_or_create(
        nome="Padrão",
        defaults={"imagem": "path/para/logo-padrao.png"}
    )
    return logo

def buscar_logo_clearbit(marca_nome):
    """
    Busca o logo no Clearbit.
    """
    dominio = marca_nome.lower() + ".com"
    url_logo = f"https://logo.clearbit.com/{dominio}"
    
    try:
        response = requests.get(url_logo)
        response.raise_for_status()
        
        logo, criado = Logo.objects.get_or_create(nome=marca_nome)
        if criado:
            logo.imagem.save(f"{marca_nome}.png", ContentFile(response.content), save=True)
            print(f"Logo para {marca_nome} adicionado com sucesso via Clearbit.")
        
        return logo
    
    except requests.exceptions.RequestException as e:
        print(f"Erro no Clearbit para {marca_nome}: {e}")
        return None

def buscar_logo_brandfetch(marca_nome):
    """
    Busca o logo em formato SVG no Brandfetch.
    """
    api_key = "ZcieYBn6Hg1UT9emBlVg3iyCYqTBttnMe7HmU+xQmQ8="  
    url = f"https://api.brandfetch.io/v2/brands/{marca_nome.lower()}.com"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        # Procurar por um logo em formato SVG
        logos = data.get("logos", [])
        svg_logo_url = next((logo["url"] for logo in logos if logo["type"] == "svg"), None)
        
        if svg_logo_url:
            response_logo = requests.get(svg_logo_url)
            response_logo.raise_for_status()
            
            logo, criado = Logo.objects.get_or_create(nome=marca_nome)
            if criado:
                logo.imagem.save(f"{marca_nome}.svg", ContentFile(response_logo.content), save=True)
                print(f"Logo SVG para {marca_nome} adicionado com sucesso via Brandfetch.")
            
            return logo
        
        print(f"Logo SVG para {marca_nome} não encontrado no Brandfetch.")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Erro no Brandfetch para {marca_nome}: {e}")
        return None


def transacoes_view(request):
    # Inicializa a queryset de transações
    transacoes = Transacao.objects.all().order_by('-data')

    # Filtro de datas
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')

    if data_inicial and data_final:
        try:
            data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
            data_final = datetime.strptime(data_final, '%Y-%m-%d')
            if data_inicial <= data_final:
                transacoes = transacoes.filter(data__gte=data_inicial, data__lte=data_final)
            else:
                messages.error(request, 'A data inicial não pode ser maior que a data final.')
        except ValueError:
            messages.error(request, 'Uma ou ambas as datas estão no formato inválido.')

    # Formulário de criação de nova transação
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            transacao = form.save(commit=False)

            # Prever marca usando modelo de ML
            titulo = transacao.titulo
            marca_prevista = modelo_ml.predict([titulo])[0]

            # Buscar ou obter o logo
            logo = Logo.objects.filter(nome__iexact=marca_prevista).first()
            if not logo:
                logo = obter_logo_via_api(marca_prevista)
            transacao.logo = logo
            transacao.save()

            messages.success(request, 'Transação adicionada com sucesso.')
            return redirect('transacoes')
        else:
            messages.error(request, 'Erro ao adicionar transação. Verifique os dados.')
    else:
        form = TransacaoForm()

    # Pegar categorias, contas e cartões para o formulário
    categorias = Categoria.objects.all()
    contas = Conta.objects.all()
    cartoes = Cartao.objects.all()

    # Renderizar o template com os dados necessários
    return render(request, 'financas/transacoes.html', {
        'transacoes': transacoes,
        'form': form,
        'data_inicial': data_inicial,
        'data_final': data_final,
        'categorias': categorias,
        'contas': contas,
        'cartoes': cartoes,
    })

def nova_transacao(request):
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            # Processa a transação
            transacao = form.save(commit=False)

            # Verifica a forma de pagamento e associa a conta ou cartão
            if 'forma_pagamento_conta' in request.POST:
                conta_id = request.POST.get('forma_pagamento_conta')
                conta = Conta.objects.get(id=conta_id)
                transacao.forma_pagamento_type = ContentType.objects.get_for_model(Conta)
                transacao.forma_pagamento_id = conta.id
            elif 'forma_pagamento_cartao' in request.POST:
                cartao_id = request.POST.get('forma_pagamento_cartao')
                cartao = Cartao.objects.get(id=cartao_id)
                transacao.forma_pagamento_type = ContentType.objects.get_for_model(Cartao)
                transacao.forma_pagamento_id = cartao.id

            transacao.save()

            messages.success(request, 'Transação criada com sucesso!')
            return redirect('transacoes')
        else:
            messages.error(request, 'Erro ao criar transação. Verifique os dados e tente novamente.')
    
    else:
        form = TransacaoForm()

    return render(request, 'financas/transacoes.html', {'form': form, 'contas': Conta.objects.all(), 'cartoes': Cartao.objects.all()})


def buscar_transacoes(request):
    try:
        query = request.GET.get('q', '')  # Captura o termo da pesquisa
        resultados = Transacao.objects.none()  # Inicia com um queryset vazio
        colunas = [
            ('titulo', 'titulo__icontains'),
            ('valor', 'valor__icontains'),
            ('data', 'data__icontains'),
            ('categoria', 'categoria__nome__icontains'),
            ('tipo', 'tipo__icontains'),
        ]

        # Testa as colunas em sequência
        for nome_coluna, filtro_coluna in colunas:
            if not resultados.exists():  # Continua apenas se não houver resultados
                print(f"Buscando em {nome_coluna} com '{query}'...")
                resultados = Transacao.objects.filter(**{filtro_coluna: query})
                if resultados.exists():
                    print(f"Resultados encontrados em {nome_coluna}: {resultados}")

        # Adiciona filtro para forma de pagamento (Cartao ou Conta)
        if not resultados.exists():
            forma_pagamento_content_types = ContentType.objects.get_for_models(Cartao, Conta).values()
            for content_type in forma_pagamento_content_types:
                resultados = Transacao.objects.filter(
                    forma_pagamento_type=content_type,
                    forma_pagamento_id__in=content_type.model_class().objects.filter(nome__icontains=query).values_list('id', flat=True)
                )
                if resultados.exists():
                    print(f"Resultados encontrados em forma de pagamento: {resultados}")
                    break

        # Serializar resultados para JSON
        dados = []
        for transacao in resultados:
            forma_pagamento_nome = ''
            if transacao.forma_pagamento:
                forma_pagamento_nome = transacao.forma_pagamento.nome

            logo_url = ''
            if transacao.logo:
                logo_url = transacao.logo.imagem.url

            dados.append({
                'titulo': transacao.titulo,
                'valor': float(transacao.valor),
                'data': transacao.data.strftime('%Y-%m-%d %H:%M:%S') if transacao.data else '',
                'categoria': transacao.categoria.nome if transacao.categoria else '',
                'tipo': transacao.tipo,
                'forma_pagamento': forma_pagamento_nome,
                'logo_url': logo_url,
                'id': transacao.id
            })

        print(f"Resultados finais: {dados}")  # Exibe os resultados encontrados
        return JsonResponse({'transacoes': dados, 'quantidade': resultados.count()})

    except Exception as e:
        # Registrar erro para debug
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def relatorios_view(request):
    analyzer = FinancialAnalyzer()
    hoje = timezone.now()

    try:
        # Obtém todas as transações
        transacoes = Transacao.objects.all()
        cartoes = Cartao.objects.all()

        # Análises básicas
        variacoes = analyzer.calculate_variation(transacoes, period='monthly')
        tendencias = analyzer.analyze_trends(transacoes)
        resumo_mensal = analyzer.get_monthly_summary(transacoes, hoje.year, hoje.month)

        # Análises por categoria
        categorias = Categoria.objects.all()
        status_orcamento = analyzer.analyze_budget_status(categorias, transacoes)

        # Projeções futuras
        projecoes, intervalos_confianca = analyzer.project_future_values(transacoes, months_ahead=12)
        
        # Análise de cartões
        analise_cartoes = {}
        for cartao in cartoes:
            transacoes_cartao = cartao.transacoes_cartao.all()
            if transacoes_cartao.exists():
                analise_cartoes[cartao.id] = {
                    'nome': cartao.nome,
                    'tendencia': analyzer.analyze_trends(transacoes_cartao),
                    'projecao': analyzer.project_future_values(
                        transacoes_cartao, 
                        months_ahead=3)[0] #Pegamos só as projeções, sem intervalo
                }
        
        # Análise de limites
        limites = Limites.objects.all()
        analise_limites = {}
        for limite in limites:
            transacoes_categoria = transacoes.filter(categoria=limite.categoria)
            if transacoes_categoria.exists():
                analise_limites[limite.id] = {
                    'titulo': limite.titulo,
                    'valor': float(limite.valor),
                    'tendencia': analyzer.analyze_trends(transacoes_categoria).value,
                    'projecao_proximos_meses': analyzer.project_future_values(
                        transacoes_categoria, 
                        months_ahead=3)[0]
                }

        # Dados para os gráficos
        expenses_over_time = analyzer.get_expenses_over_time(transacoes, period='daily')
        expenses_by_category = analyzer.get_expenses_by_category(transacoes)
        financial_balance = analyzer.get_financial_balance(transacoes)

        context = {
            'variacoes': variacoes,
            'tendencias': {k: v.value for k, v in tendencias.items()},
            'resumo_mensal': resumo_mensal,
            'projecoes': projecoes,
            'intervalos_confianca': intervalos_confianca,
            'status_orcamento': status_orcamento,
            'analise_cartoes': analise_cartoes,
            'analise_limites': analise_limites,
            'mes_atual': hoje.strftime("%B %Y"),
            'expenses_over_time': expenses_over_time,
            'expenses_by_category': expenses_by_category,
            'financial_balance': financial_balance,
            'erro': None
        }
        
    except Exception as e:
        context = {
            'erro': f"Erro ao gerar relatórios: {str(e)}",
            'mes_atual': hoje.strftime("%B %Y")
        }

    return render(request, 'financas/relatorios.html', context)

def exportar_relatorio(request):
    """View para exportar relatório em formato JSON"""
    analyzer = FinancialAnalyzer()
    
    try:
        transacoes = Transacao.objects.all()
        categorias = Categoria.objects.all()
        hoje = timezone.now()
        
        dados_relatorio = {
            'data_geracao': hoje.isoformat(),
            'resumo_mensal': analyzer.get_monthly_summary(
                transacoes,
                hoje.year,
                hoje.month
            ),
            'variacoes': analyzer.calculate_variation(transacoes),
            'tendencias': {k: v.value for k, v in analyzer.analyze_trends(transacoes).items()},
            'status_orcamento': analyzer.analyze_budget_status(categorias, transacoes),
            'totais': {
                'receitas': float(transacoes.filter(tipo='RECEITA').aggregate(sum('valor'))['valor__sum'] or 0),
                'despesas': float(transacoes.filter(tipo='DESPESA').aggregate(sum('valor'))['valor__sum'] or 0)
            }
        }
        
        # Configura a resposta HTTP como um arquivo para download
        response = JsonResponse(dados_relatorio)
        response['Content-Disposition'] = 'attachment; filename="relatorio_financeiro.json"'
        return response
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

def lista_metas_view(request):
    metas = Meta.objects.all()
    categorias = Categoria.objects.all()
    context = {
        'metas': metas,
        'categorias': categorias
    }
    return render(request, 'financas/metas.html', context)

def criar_meta_view(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        valor_meta = request.POST.get('valor_meta')
        categoria_id = request.POST.get('categoria')
        imagem = request.FILES.get('imagem')

        try:
            categoria = Categoria.objects.get(id=categoria_id) if categoria_id else None
            
            Meta.objects.create(
                titulo=titulo,
                valor_meta=valor_meta,
                valor_atual=0,  # Inicializa com 0
                categoria=categoria,
                imagem=imagem
            )
            messages.success(request, 'Meta criada com sucesso!')
            return redirect('lista-metas')
        except Exception as e:
            messages.error(request, 'Erro ao criar meta. Verifique os dados e tente novamente.')
    
    return redirect('metas')

@csrf_exempt  # Para testes locais; em produção, use o middleware CSRF
def atualizar_meta(request, meta_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # Decodifica o JSON recebido
            valor_meta = data.get('valor_meta')  # Obtém o campo 'valor_meta'

            print("Valor recebido no backend:", valor_meta)


            if valor_meta is None:  # Validação
                return JsonResponse({'error': 'O campo valor_meta é obrigatório.'}, status=400)

            meta = Meta.objects.get(id=meta_id)
            meta.valor_atual += float(valor_meta)  # Atualiza o valor atual
            meta.save()

            return JsonResponse({'success': True, 'nova_meta': meta.valor_atual})
        except Meta.DoesNotExist:
            return JsonResponse({'error': 'Meta não encontrada.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)

def editar_meta_view(request, meta_id):
    try:
        meta = Meta.objects.get(id=meta_id)
    except Meta.DoesNotExist:
        return JsonResponse({'error': 'Meta não encontrada.'}, status=404)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        valor_meta = request.POST.get('valor_meta')
        categoria_id = request.POST.get('categoria')
        imagem = request.FILES.get('imagem')

        try:
            categoria = Categoria.objects.get(id=categoria_id) if categoria_id else None

            meta.titulo = titulo
            meta.valor_meta = valor_meta
            meta.categoria = categoria
            if imagem:
                meta.imagem = imagem
            meta.save()

            return JsonResponse({'success': True, 'nova_titulo': meta.titulo, 'nova_valor': meta.valor_meta})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método não permitido.'}, status=405)

def excluir_meta_view(request, meta_id):
    try:
        meta = Meta.objects.get(id=meta_id)
        meta.delete()
        messages.success(request, 'Meta excluída com sucesso!')
    except Meta.DoesNotExist:
        messages.error(request, 'Meta não encontrada.')
    except Exception as e:
        messages.error(request, 'Erro ao excluir a meta. Tente novamente.')

    return redirect('lista-metas')


def pagamentos_lista(request):
    hoje = timezone.now().date()

    # Primeiro e último dia do mês
    primeiro_dia_mes = hoje.replace(day=1)
    ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Filtrar pagamentos
    pagamentos_hoje = Pagamento.objects.filter(data_vencimento=hoje)
    pagamentos_semana = Pagamento.objects.filter(
        data_vencimento__range=[hoje + timedelta(days=1), hoje + timedelta(days=7)]
    )
    pagamentos_mes = Pagamento.objects.filter(
        data_vencimento__range=[hoje + timedelta(days=1), ultimo_dia_mes]
    )  # Apenas futuros deste mês
    pagamentos_atrasados = Pagamento.objects.filter(
        data_vencimento__lt=hoje,
        data_vencimento__gte=primeiro_dia_mes,
        status='pendente'
    )

    context = {
        'pagamentos_hoje': pagamentos_hoje,
        'pagamentos_semana': pagamentos_semana,
        'pagamentos_mes': pagamentos_mes,
        'pagamentos_atrasados': pagamentos_atrasados,
        'total_pagamentos_mes': pagamentos_mes.count(),
        'valor_total_mes': sum(p.valor for p in pagamentos_mes),
    }

    return render(request, 'financas/pagamentos.html', context)



def adicionar_pagamento(request):
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            try:
                pagamento = form.save(commit=False)
                pagamento.save()
                return JsonResponse({'status': 'success'})
            except Exception as e:
                # Log do erro no console para depuração
                print(f"Erro ao salvar pagamento: {e}")
                return JsonResponse({'status': 'error', 'errors': 'Erro interno no servidor.'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

def pagar_conta(request):
    if request.method == 'POST':
        # Pega os dados do POST
        pagamento_id = request.POST.get('pagamento_id')
        tipo_entidade = request.POST.get('tipo')  # 'conta' ou 'cartao'
        entidade_id = request.POST.get('entidade_id')  # ID da Conta ou do Cartão

        # Valida os dados
        if not pagamento_id or not tipo_entidade or not entidade_id:
            return JsonResponse({'status': 'error', 'message': 'Dados incompletos'}, status=400)

        pagamento = get_object_or_404(Pagamento, id=pagamento_id)

        if tipo_entidade == 'conta':
            conta = get_object_or_404(Conta, id=entidade_id)
            if conta.saldo < pagamento.valor:
                return JsonResponse({'status': 'error', 'message': 'Saldo insuficiente'}, status=400)

            # Deduz o valor do saldo
            conta.saldo -= pagamento.valor
            conta.save()
        elif tipo_entidade == 'cartao':
            cartao = get_object_or_404(Cartao, id=entidade_id)
            if cartao.limite < pagamento.valor:
                return JsonResponse({'status': 'error', 'message': 'Limite insuficiente'}, status=400)

            # Deduz o valor do limite
            cartao.limite -= pagamento.valor
            cartao.save()
        else:
            return JsonResponse({'status': 'error', 'message': 'Tipo de entidade inválido'}, status=400)

        # Atualiza o status do pagamento
        pagamento.status = 'pago'
        pagamento.save()

        # Retorna uma resposta de sucesso
        return JsonResponse({'status': 'success', 'message': 'Pagamento realizado com sucesso'})

    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

def api_detalhe_pagamento(request, pagamento_id):
    pagamento = get_object_or_404(Pagamento, id=pagamento_id)
    return JsonResponse({
        'id': pagamento.id,
        'titulo': pagamento.titulo,
        'valor': pagamento.valor,
        'data_vencimento': pagamento.data_vencimento.isoformat(),
    })

def api_contas_cartoes_disponiveis(request):
    if request.method == 'GET':
        # Buscando contas associadas aos bancos
        contas = Conta.objects.all().select_related('banco')
        cartoes = Cartao.objects.all().select_related('banco')

        # Construindo a lista de contas
        contas_data = [
            {
                'id': conta.id,
                'tipo': 'Conta Corrente',
                'nome': conta.titulo,
                'saldo': float(conta.saldo),  # Convertendo Decimal para float para compatibilidade JSON
                'banco': conta.banco.nome if conta.banco else 'Sem Banco',
            }
            for conta in contas
        ]

        # Construindo a lista de cartões
        cartoes_data = [
            {
                'id': cartao.id,
                'tipo': 'Cartão de Crédito',
                'nome': cartao.nome_cartao,
                'limite': float(cartao.limite_total),  # Convertendo Decimal para float para compatibilidade JSON
                'banco': cartao.banco.nome if cartao.banco else 'Sem Banco',
            }
            for cartao in cartoes
        ]

        # Combinando contas e cartões
        contas_cartoes = contas_data + cartoes_data

        return JsonResponse(contas_cartoes, safe=False)

    return JsonResponse({"error": "Método não permitido"}, status=405)



def plano_de_gastos_view(request):
    analyzer = FinancialAnalyzer()
    hoje = timezone.now()
    mes_atual = hoje.strftime("%B %Y")

    try:
        categorias = Categoria.objects.all()
        transacoes = Transacao.objects.all()

        status_orcamento = analyzer.analyze_budget_status(categorias, transacoes)
        tendencias = analyzer.analyze_trends(transacoes)
        resultado_projecoes = analyzer.project_future_values(transacoes, months_ahead=12)
        projecoes_futuras = resultado_projecoes[0]
        intervalos_confianca = resultado_projecoes[1]

        categoria_data = [{
            'nome': cat.nome,
            'valor': float(cat.valor_total),
            'cor': cat.cor,
            'orcamento': float(cat.orcamento),
            'percentual_usado': status_orcamento[cat.nome]['percentual_usado'],
            'disponivel': status_orcamento[cat.nome]['disponivel'],
            'tendencia': tendencias.get(cat.nome, 'STABLE').value
        } for cat in categorias]

        orcamento_total = sum(cat.orcamento for cat in categorias)
        gastos_total = sum(cat.valor_total for cat in categorias)
        saldo_restante = orcamento_total - gastos_total

        despesas = DespesaPlanejada.objects.all()
        despesas_data = [{
            'id': desp.id,
            'nome': desp.nome,
            'cor': desp.cor,
            'valor_total': float(desp.valor_total),
            'valor_gasto': float(desp.valor_gasto),
            'valor_faltante': float(desp.valor_faltante),
            'percentual_gasto': desp.percentual_gasto,
            'projecao_proximos_meses': projecoes_futuras.get(desp.nome, [])
        } for desp in despesas]

        context = {
            'mes_atual': mes_atual,
            'categorias': categorias,
            'orcamento_total': orcamento_total,
            'gastos_total': gastos_total,
            'saldo_restante': saldo_restante,
            'despesas_planejadas': despesas,
            'categoria_data': json.dumps(categoria_data),
            'despesas_data': json.dumps(despesas_data),
            'status_orcamento': status_orcamento,
            'tendencias': {k: v.value for k, v in tendencias.items()},
            'projecoes': projecoes_futuras,
            'intervalos_confianca': intervalos_confianca
        }

    except Exception as e:
        context = {
            'mes_atual': mes_atual,
            'erro': f"Erro ao processar dados: {str(e)}"
        }

    return render(request, 'financas/plano_de_gastos.html', context)

def carteira_views(request):
    context = {
        'contas': Conta.objects.all(),
        'bancos': Banco.objects.all(),
        'cartoes': Cartao.objects.all(),
        'dias': range(1, 32),
        'conta_form': ContaForm(),  # Formulário vazio para renderizar a página inicial
        'cartao_form': CartaoForm(),
        'transacao_form': TransacaoCartaoForm(),
    }

    return render(request, 'financas/meus_cartoes.html', context)


def adicionar_conta(request):
    if request.method == 'POST':
        conta_form = ContaForm(request.POST)
        print("Dados recebidos:", request.POST)

        if conta_form.is_valid():
            conta_form.save()
            messages.success(request, 'Conta criada com sucesso!')
        else:
            print("Erros de validação:", conta_form.errors)
            messages.error(request, 'Erro ao criar conta. Verifique os dados e tente novamente.')
    return redirect('meus_cartoes')


def adicionar_cartao(request):
    if request.method == 'POST':
        cartao_form = CartaoForm(request.POST)
        if cartao_form.is_valid():
            cartao = cartao_form.save(commit=False)
            try:
                banco_id = request.POST.get('banco')
                cartao.banco = Banco.objects.get(id=banco_id)
                cartao.save()
                messages.success(request, 'Cartão adicionado com sucesso!')
            except Banco.DoesNotExist:
                messages.error(request, 'Banco não encontrado.')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro inesperado: {e}')
        else:
            print("Erros de validação:", cartao_form.errors)
            messages.error(request, 'Erro ao adicionar cartão. Verifique os dados.')
    return redirect('meus_cartoes')



def pagar_fatura(request, cartao_id):
    """View para realizar o pagamento de uma fatura."""
    cartao = get_object_or_404(Cartao, id=cartao_id)  # Remove a verificação de usuário.

    if request.method == 'POST':
        # Lógica de pagamento
        cartao.saldo -= cartao.valor_fatura  # Exemplo: subtraindo o valor da fatura do saldo
        cartao.valor_fatura = 0  # Zera a fatura após o pagamento
        cartao.save()

        messages.success(request, 'Fatura paga com sucesso!')
        return JsonResponse({'status': 'success', 'message': 'Fatura paga com sucesso!'})

    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


def transacoes_cartao(request, cartao_id):
    """View para listar e gerenciar transações de um cartão."""
    cartao = get_object_or_404(Cartao, id=cartao_id)  # Remove a verificação de usuário.
    transacoes = cartao.transacoes_cartao.all()  # `related_name` do relacionamento entre cartão e transações.

    # Filtros de data
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')

    if data_inicial and data_final:
        transacoes = transacoes.filter(data__range=[data_inicial, data_final])

    transacao_form = TransacaoCartaoForm()

    if request.method == 'POST':
        transacao_form = TransacaoCartaoForm(request.POST)
        if transacao_form.is_valid():
            transacao = transacao_form.save(commit=False)
            transacao.cartao = cartao
            transacao.save()

            messages.success(request, 'Transação adicionada com sucesso!')
            return redirect('transacoes_cartao', cartao_id=cartao.id)
        else:
            messages.error(request, 'Erro ao adicionar transação. Verifique os dados.')

    context = {
        'cartao': cartao,
        'transacoes': transacoes,
        'transacao_form': transacao_form,
    }

    return render(request, 'financas/transacoes_cartao.html', context)


def meus_limites(request):
    return render(request, 'financas/meus_limites.html')

def novo_limite(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        titulo = request.POST.get('titulo')
        valor = request.POST.get('valor')
        recorrencia = request.POST.get('recorrencia')
        data_inicio = request.POST.get('data_inicio')
        
        
        categoria = Categoria.objects.get(id=categoria_id)
        
        
        Limites.objects.create(
            categoria=categoria,
            titulo=titulo,
            valor=valor,
            recorrencia=recorrencia,
            data_inicio=data_inicio
        )
        
        return redirect('dashboard')
    
    
    categories = Categoria.objects.all().order_by('name')
    return render(request, 'limits/novo_limite.html', {'categories': categories})

# API view to get categories (optional - for dynamic loading)
def get_categories(request):
    categories = Categoria.objects.all().order_by('name')
    return JsonResponse({
        'categories': list(categories.values('id', 'name', 'icon'))
    })


def listar_categorias(request):
    categorias_usuario = Categoria.objects.filter(padrao=False)
    categorias_padrao = Categoria.objects.filter(padrao=True)
    formulario = CategoriaForm()
    
    contexto = {
        'categorias_usuario': categorias_usuario,
        'categorias_padrao': categorias_padrao,
        'formulario': formulario,
    }
    return render(request, 'financas/categorias.html', contexto)

def criar_categoria(request):
    if request.method == 'POST':
        formulario = CategoriaForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('categorias')
        else:
            messages.error(request, "Erro ao criar a categoria. Verifique os dados do formulário.")
    return redirect('categorias')

def adicionar_limite(request):
    if request.method == 'POST':
        nome_categoria = request.POST.get('categoria_nome')
        valor = request.POST.get('valor')
        recorrencia = request.POST.get('recorrencia')

        # Lógica para salvar o limite da categoria
        # Exemplo:
        # categoria = Categoria.objects.get(nome=nome_categoria)
        # categoria.limite = valor
        # categoria.recorrencia = recorrencia
        # categoria.save()

        messages.success(request, 'Limite adicionado com sucesso!')
        return redirect('categoiras')

    return redirect('categorias')


# API view to get subcategories (optional - for dynamic loading)
def get_subcategories(request):
    subcategories = Subcategoria.objects.all().order_by('name')
    return JsonResponse({
        'subcategories': list(subcategories.values('id', 'name', 'icon'))
    })


def listar_subcategorias(request):
    subcategorias_usuario = Subcategoria.objects.filter(padrao=False)
    subcategorias_padrao = Subcategoria.objects.filter(padrao=True)
    formulario = SubcategoriaForm()
    
    contexto = {
        'subcategorias_usuario': subcategorias_usuario,
        'subcategorias_padrao': subcategorias_padrao,
        'formulario': formulario,
    }
    return render(request, 'financas/subcategorias.html', contexto)

def criar_subcategoria(request):
    if request.method == 'POST':
        formulario = SubcategoriaForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('subcategorias')
        else:
            messages.error(request, "Erro ao criar a subcategoria. Verifique os dados do formulário.")
    return redirect('subcategorias')

def get_expenses_over_time(request, period):
    analyzer = FinancialAnalyzer()
    transacoes = Transacao.objects.all()
    expenses = analyzer.get_expenses_over_time(transacoes, period)
    return JsonResponse({'expenses': expenses})

def get_expenses_by_category(request):
    analyzer = FinancialAnalyzer()
    transacoes = Transacao.objects.all()
    expenses_by_category = analyzer.get_expenses_by_category(transacoes)
    return JsonResponse({'expenses_by_category': expenses_by_category})

def get_financial_balance(request):
    analyzer = FinancialAnalyzer()
    transacoes = Transacao.objects.all()
    balance = analyzer.get_financial_balance(transacoes)
    return JsonResponse(balance)
