import numpy as np
from typing import List, Dict, Tuple
from enum import Enum
from decimal import Decimal
from django.db.models import QuerySet
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractDay, ExtractWeek
from django.db.models import Sum
from datetime import datetime

class TrendType(Enum):
    """Enum para classificar tendências"""
    ASCENDING = "Crescente"
    DESCENDING = "Decrescente"
    STABLE = "Estável"
    VOLATILE = "Volátil"

class FinancialAnalyzer:
    """Classe para análise financeira integrada com os modelos Django"""
    
    def __init__(self):
        self._precision = 2

    def _convert_to_float(self, value: Decimal) -> float:
        return float(value)

    def _decimal_to_float_list(self, values: List[Decimal]) -> List[float]:
        return [self._convert_to_float(v) for v in values]

    def calculate_variation(self, queryset: QuerySet, period: str = 'monthly') -> Dict[str, List[float]]:
        """
        Calcula variação percentual de transações por período
        
        Args:
            queryset: QuerySet de Transacao
            period: 'monthly' ou 'yearly'
        """
        try:
            transactions = queryset.values('data', 'valor', 'tipo')
            
            # Agrupa transações por período
            period_totals = {}
            for trans in transactions:
                date = trans['data']
                if period == 'monthly':
                    period_key = f"{date.year}-{date.month:02d}"
                else:
                    period_key = str(date.year)
                
                if period_key not in period_totals:
                    period_totals[period_key] = {
                        'RECEITA': Decimal('0'),
                        'DESPESA': Decimal('0')
                    }
                
                period_totals[period_key][trans['tipo']] += trans['valor']

            # Organiza os períodos cronologicamente
            sorted_periods = sorted(period_totals.items())
            
            # Calcula variações para receitas e despesas
            variations = {'RECEITA': [], 'DESPESA': []}
            for i in range(1, len(sorted_periods)):
                prev_period = sorted_periods[i-1][1]
                curr_period = sorted_periods[i][1]
                
                for tipo in ['RECEITA', 'DESPESA']:
                    if prev_period[tipo] != 0:
                        var = ((curr_period[tipo] - prev_period[tipo]) / prev_period[tipo]) * 100
                        variations[tipo].append(round(float(var), self._precision))

            return variations
        except Exception as e:
            raise ValueError(f"Erro no cálculo de variações: {str(e)}")

    def calculate_average_by_category(self, queryset: QuerySet, period: str = 'monthly') -> Dict[str, float]:
        """
        Calcula média de valores por categoria
        
        Args:
            queryset: QuerySet de Transacao
            period: 'monthly' ou 'yearly'
        """
        try:
            # Agrupa e calcula média por categoria
            averages = queryset.values('categoria').annotate(avg_valor=Sum('valor'))
            
            return {
                item['categoria']: round(float(item['avg_valor']), self._precision)
                for item in averages
            }
        except Exception as e:
            raise ValueError(f"Erro no cálculo de médias: {str(e)}")

    def project_future_values(self, queryset: QuerySet, 
                            months_ahead: int = 12) -> Tuple[Dict[str, List[float]], Dict[str, List[Tuple[float, float]]]]:
        """
        Projeta valores futuros com base no histórico
        
        Args:
            queryset: QuerySet de Transacao
            months_ahead: Número de meses a projetar
        
        Returns:
            Tupla com (projeções por categoria, intervalos de confiança)
        """
        try:
            projections = {}
            confidence_intervals = {}
        
            # Agrupa por categoria
            for categoria in queryset.values_list('categoria', flat=True).distinct():
                cat_transactions = queryset.filter(categoria=categoria).order_by('data')
                values = [float(v) for v in cat_transactions.values_list('valor', flat=True)]
            
                if len(values) < 4:  # Precisa de pelo menos 4 pontos para projeção
                    continue
            
                # Prepara dados para projeção
                data = np.array(values)
                x = np.arange(len(data))
            
                # Calcula tendência linear
                z = np.polyfit(x, data, 1)
                slope, intercept = z[0], z[1]
            
                # Projeta valores futuros
                future_x = np.arange(len(data), len(data) + months_ahead)
                projected = slope * future_x + intercept
            
                # Calcula intervalo de confiança
                std_dev = np.std(data - (slope * x + intercept))
                confidence = 1.96 * std_dev  # 95% de confiança
            
                # Armazena usando o ID da categoria como inteiro
                projections[categoria] = projected.tolist()
                confidence_intervals[categoria] = [
                    (v - confidence, v + confidence) for v in projected
                ]
        
            return projections, confidence_intervals
        except Exception as e:
            raise ValueError(f"Erro na projeção de valores: {str(e)}")

    def analyze_trends(self, queryset: QuerySet, window_size: int = 3) -> Dict[str, TrendType]:
        """
        Analisa tendências por categoria
        
        Args:
            queryset: QuerySet de Transacao
            window_size: Tamanho da janela para média móvel
        """
        try:
            trends = {}
            
            # Analisa cada categoria separadamente
            for categoria in queryset.values_list('categoria', flat=True).distinct():
                cat_transactions = queryset.filter(categoria=categoria).order_by('data')
                values = [float(v) for v in cat_transactions.values_list('valor', flat=True)]
                
                if len(values) < window_size:
                    continue
                
                # Calcula média móvel
                data = np.array(values)
                weights = np.ones(window_size) / window_size
                moving_avg = np.convolve(data, weights, mode='valid')
                
                # Analisa tendência
                variations = np.diff(moving_avg)
                volatility = np.std(variations)
                mean_variation = np.mean(variations)
                
                # Define limiares
                volatility_threshold = np.mean(np.abs(data)) * 0.1
                trend_threshold = np.mean(np.abs(data)) * 0.05
                
                # Classifica tendência
                if volatility > volatility_threshold:
                    trends[categoria] = TrendType.VOLATILE
                elif mean_variation > trend_threshold:
                    trends[categoria] = TrendType.ASCENDING
                elif mean_variation < -trend_threshold:
                    trends[categoria] = TrendType.DESCENDING
                else:
                    trends[categoria] = TrendType.STABLE
            
            return trends
        except Exception as e:
            raise ValueError(f"Erro na análise de tendências: {str(e)}")

    def analyze_budget_status(self, categoria_queryset, transacao_queryset) -> Dict[str, Dict]:
        """
        Analisa status do orçamento por categoria
        
        Args:
            categoria_queryset: QuerySet de Categoria
            transacao_queryset: QuerySet de Transacao
        """
        try:
            status = {}
        
            for categoria in categoria_queryset:
                # Pega total de despesas da categoria usando o ID
                total_despesas = transacao_queryset.filter(
                    categoria=categoria,  # Usa o objeto categoria em vez do nome
                    tipo='DESPESA'
                ).aggregate(total=Sum('valor'))['total'] or Decimal('0')
            
                # Calcula percentual do orçamento utilizado
                if categoria.orcamento > 0:
                    percentual_usado = (total_despesas / categoria.orcamento) * 100
                else:
                    percentual_usado = 0
            
                status[categoria.nome] = {
                    'orcamento': float(categoria.orcamento),
                    'gasto': float(total_despesas),
                    'percentual_usado': round(float(percentual_usado), 1),
                    'disponivel': float(categoria.orcamento - total_despesas)
                }
        
            return status
        except Exception as e:
            raise ValueError(f"Erro na análise do orçamento: {str(e)}")

    def get_monthly_summary(self, queryset: QuerySet, year: int, month: int) -> Dict:
        """
        Gera resumo financeiro mensal
        
        Args:
            queryset: QuerySet de Transacao
            year: Ano do resumo
            month: Mês do resumo
        """
        try:
            # Filtra transações do mês
            monthly_transactions = queryset.filter(
                data__year=year,
                data__month=month
            )
            
            # Calcula totais
            receitas = monthly_transactions.filter(tipo='RECEITA').aggregate(
                total=Sum('valor'))['total'] or Decimal('0')
            despesas = monthly_transactions.filter(tipo='DESPESA').aggregate(
                total=Sum('valor'))['total'] or Decimal('0')
            
            # Calcula por categoria
            categoria_summary = {}
            for categoria in monthly_transactions.values_list('categoria', flat=True).distinct():
                cat_total = monthly_transactions.filter(categoria=categoria).aggregate(
                    total=Sum('valor'))['total'] or Decimal('0')
                categoria_summary[categoria] = float(cat_total)
            
            return {
                'receitas': float(receitas),
                'despesas': float(despesas),
                'saldo': float(receitas - despesas),
                'por_categoria': categoria_summary
            }
        except Exception as e:
            raise ValueError(f"Erro na geração do resumo mensal: {str(e)}")

    def get_expenses_over_time(self, queryset: QuerySet, period: str = 'daily') -> List[float]:
        """
        Obtém os gastos ao longo do tempo.
        
        Args:
            queryset: QuerySet de Transacao
            period: 'daily', 'weekly', 'biweekly', 'monthly'
        """
        try:
            transactions = queryset.filter(tipo='DESPESA').values('data', 'valor')
            expenses = []

            if period == 'daily':
                expenses = transactions.annotate(day=ExtractDay('data')).values('day').annotate(total=Sum('valor')).order_by('day')
            elif period == 'weekly':
                expenses = transactions.annotate(week=ExtractWeek('data')).values('week').annotate(total=Sum('valor')).order_by('week')
            elif period == 'biweekly':
                expenses = transactions.annotate(week=ExtractWeek('data')).values('week').annotate(total=Sum('valor')).order_by('week')
                expenses = [sum(expenses[i:i+2]) for i in range(0, len(expenses), 2)]
            elif period == 'monthly':
                expenses = transactions.annotate(month=ExtractMonth('data')).values('month').annotate(total=Sum('valor')).order_by('month')

            return [float(expense['total']) for expense in expenses]
        except Exception as e:
            raise ValueError(f"Erro ao obter gastos ao longo do tempo: {str(e)}")

    def get_expenses_by_category(self, queryset: QuerySet) -> Dict[str, float]:
        """
        Obtém os gastos por categoria.
        
        Args:
            queryset: QuerySet de Transacao
        """
        try:
            transactions = queryset.filter(tipo='DESPESA').values('categoria__nome').annotate(total=Sum('valor')).order_by('categoria__nome')
            return {trans['categoria__nome']: float(trans['total']) for trans in transactions}
        except Exception as e:
            raise ValueError(f"Erro ao obter gastos por categoria: {str(e)}")

    def get_financial_balance(self, queryset: QuerySet) -> Dict[str, List[float]]:
        """
        Obtém o balanço financeiro (receitas vs despesas).
        
        Args:
            queryset: QuerySet de Transacao
        """
        try:
            transactions = queryset.values('data', 'valor', 'tipo')
            balance = {'labels': [], 'income': [], 'expenses': []}

            monthly_transactions = transactions.annotate(month=ExtractMonth('data'), year=ExtractYear('data')).values('year', 'month', 'tipo').annotate(total=Sum('valor')).order_by('year', 'month')

            for trans in monthly_transactions:
                label = f"{trans['year']}-{trans['month']:02d}"
                if label not in balance['labels']:
                    balance['labels'].append(label)
                    balance['income'].append(0)
                    balance['expenses'].append(0)

                index = balance['labels'].index(label)
                if trans['tipo'] == 'RECEITA':
                    balance['income'][index] += float(trans['total'])
                else:
                    balance['expenses'][index] += float(trans['total'])

            return balance
        except Exception as e:
            raise ValueError(f"Erro ao obter balanço financeiro: {str(e)}")