# financas/urls.py
from django.urls import path
from . import views

urlpatterns = [

    # Página inicial
    path('', views.inicio_view, name='inicio'),

    # Página de transações
    path('transacoes/', views.transacoes_view, name='transacoes'),
    path('transacoes/nova-transacao/', views.nova_transacao, name='nova_transacao'),
    path('buscar-transacoes/', views.buscar_transacoes, name='buscar-transacoes'),

    # Página de relatórios
    path('relatorios/', views.relatorios_view, name='relatorios'),
    path('get_expenses_over_time/<str:period>/', views.get_expenses_over_time, name='get_expenses_over_time'),
    path('get_expenses_by_category/', views.get_expenses_by_category, name='get_expenses_by_category'),
    path('get_financial_balance/', views.get_financial_balance, name='get_financial_balance'),

    # Rota para listagem de metas
    path('metas/', views.lista_metas_view, name='metas'), 
    path('metas/criar/', views.criar_meta_view, name='criar-meta'), 
    path('metas/atualizar-meta/<int:meta_id>/', views.atualizar_meta, name='atualizar-meta'),
    path('metas/editar/<int:meta_id>/', views.editar_meta_view, name='editar-meta'),
    path('metas/excluir/<int:meta_id>/', views.excluir_meta_view, name='excluir-meta'),

    # Página de plano de gastos

    # pagina de pagamentos
    path('pagamentos/', views.pagamentos_lista, name='pagamentos'),
    path('pagamentos/adicionar/', views.adicionar_pagamento, name='adicionar_pagamento'),
    path('pagamentos/pagar_conta/', views.pagar_conta, name='pagar_conta'),
    path('api/pagamento/<int:pagamento_id>/', views.api_detalhe_pagamento, name='api_detalhe_pagamento'),
    path('api/contas_cartoes_disponiveis/', views.api_contas_cartoes_disponiveis, name='api_contas_cartoes_disponiveis'),

    # Endpoints para ações específicas
    path('carteira/', views.carteira_views, name='meus_cartoes'),
    path('carteira/conta/adicionar/', views.adicionar_conta, name='adicionar_conta'),
    path('carteira/cartao/adicionar/', views.adicionar_cartao, name='adicionar_cartao'),

    # Operações em cartões
    path('carteira/cartao/<int:cartao_id>/pagar/', views.pagar_fatura, name='pagar_fatura'),
    path('carteira/cartao/<int:cartao_id>/transacoes/', views.transacoes_cartao, name='transacoes_cartao'),

    path('categorias/', views.listar_categorias, name='categorias'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
    path('categorias/limites/', views.adicionar_limite, name='adicionar_limite'),
    path('subcategorias/', views.listar_subcategorias, name='subcategorias'),
    path('subcategorias/criar/', views.criar_subcategoria, name='criar_subcategoria'),
    path('meus-limites/', views.meus_limites, name='meus_limites'),
]
