// Função para abrir o modal de "Novo Pagamento"
function abrirModalNovoPagamento() {
    const modal = document.getElementById('modalNovoPagamento');
    if (modal) modal.style.display = 'block';
}

// Função para fechar o modal de "Novo Pagamento"
function fecharModalNovoPagamento() {
    const modal = document.getElementById('modalNovoPagamento');
    if (modal) modal.style.display = 'none';
}

// Função para salvar novo pagamento
async function salvarNovoPagamento(event) {
    event.preventDefault();
    const form = event.target;
    const url = form.getAttribute('data-url'); // Obtém a URL gerada no HTML
    const formData = new FormData(form);

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        });

        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'success') {
            alert('Pagamento salvo com sucesso!');
            fecharModalNovoPagamento();
            location.reload();
        } else {
            handleFormErrors(data.errors);
        }
    } catch (error) {
        console.error('Erro ao salvar pagamento:', error);
        alert('Ocorreu um erro ao processar a requisição. Tente novamente.');
    }
}

// Função para abrir o modal de "Pagar Conta"
function abrirModalPagarConta(pagamentoId) {
    console.log('Abrindo modal para pagamento ID:', pagamentoId);

    fetch(`/api/pagamento/${pagamentoId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar os dados do pagamento');
            }
            return response.json();
        })
        .then(dadosPagamento => {
            console.log('Dados do pagamento recebidos:', dadosPagamento);

            // Preenche os campos do modal
            document.getElementById('titulo').value = dadosPagamento.titulo || '';
            document.getElementById('valor').value = dadosPagamento.valor || '';
            document.getElementById('data_vencimento').value = dadosPagamento.data_vencimento || '';
            document.getElementById('formPagarConta').setAttribute('data-pagamento-id', pagamentoId);

            // Carrega as opções de contas/cartões disponíveis
            fetch('/api/contas_cartoes_disponiveis/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao carregar contas/cartões');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Contas/cartões disponíveis:', data);
                    const seletor = document.getElementById('conta_cartao');
                    seletor.innerHTML = ''; // Limpa o seletor

                    // Mostra as opções de acordo com o tipo selecionado (conta ou cartão)
                    const tipoSelecionado = document.querySelector('input[name="tipo"]:checked').value;

                    const opcoesFiltradas = data.filter(item =>
                        (tipoSelecionado === 'conta' && item.tipo === 'Conta Corrente') ||
                        (tipoSelecionado === 'cartao' && item.tipo === 'Cartão de Crédito')
                    );

                    if (opcoesFiltradas.length === 0) {
                        seletor.innerHTML = '<option value="">Nenhuma opção disponível</option>';
                    } else {
                        opcoesFiltradas.forEach(item => {
                            const option = document.createElement('option');
                            option.value = item.id;
                            option.textContent = `${item.nome} - ${item.banco} (${item.saldo || item.limite})`;
                            seletor.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Erro ao carregar contas/cartões:', error);
                    alert('Não foi possível carregar as opções de contas ou cartões.');
                });

            // Exibe o modal
            document.getElementById('modalPagarConta').style.display = 'block';
        })
        .catch(error => {
            console.error('Erro ao carregar pagamento:', error);
            alert('Não foi possível carregar os dados do pagamento.');
        });
}

// Função para processar o pagamento
function processarPagamento(event) {
    event.preventDefault(); // Impede o comportamento padrão de envio do formulário

    const pagamentoId = document.getElementById('formPagarConta').getAttribute('data-pagamento-id');
    const tipoSelecionado = document.querySelector('input[name="tipo"]:checked').value;
    const contaCartaoId = document.getElementById('conta_cartao').value;

    if (!contaCartaoId) {
        alert('Selecione uma conta ou cartão antes de continuar.');
        return;
    }

    const formData = new FormData();
    formData.append('pagamento_id', pagamentoId);
    formData.append('tipo', tipoSelecionado);
    formData.append('entidade_id', contaCartaoId);

    fetch('/pagamentos/pagar_conta/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                fecharModalPagarConta();
                location.reload(); // Atualiza a página para refletir as mudanças
            } else {
                alert(data.message || 'Erro ao processar pagamento.');
            }
        })
        .catch(error => {
            console.error('Erro ao processar pagamento:', error);
            alert('Erro ao processar pagamento.');
        });
}

// Função para obter o token CSRF
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return csrfToken;
}

// Função para fechar o modal "Pagar Conta"
function fecharModalPagarConta() {
    document.getElementById('modalPagarConta').style.display = 'none';
}

// Adiciona eventos para alterar a lista de opções (contas/cartões) ao mudar o tipo
document.querySelectorAll('input[name="tipo"]').forEach(radio => {
    radio.addEventListener('change', () => {
        const pagamentoId = document.getElementById('formPagarConta').getAttribute('data-pagamento-id');
        abrirModalPagarConta(pagamentoId); // Recarrega as opções com base no tipo selecionado
    });
});

document.addEventListener('DOMContentLoaded', () => {
    // Obter os inputs de radio e os grupos de conta/cartão
    const radios = document.querySelectorAll('input[name="tipo"]');
    const grupoConta = document.getElementById('grupo-conta');
    const grupoCartao = document.getElementById('grupo-cartao');

    // Função para atualizar a exibição
    const atualizarExibicao = () => {
        const selecionado = document.querySelector('input[name="tipo"]:checked').value;
        if (selecionado === 'conta') {
            grupoConta.style.display = 'block';
            grupoCartao.style.display = 'none';
        } else if (selecionado === 'cartao') {
            grupoConta.style.display = 'none';
            grupoCartao.style.display = 'block';
        }
    };

    // Adicionar evento de mudança a todos os rádios
    radios.forEach(radio => {
        radio.addEventListener('change', atualizarExibicao);
    });

    // Chamar a função inicialmente para configurar o estado inicial
    atualizarExibicao();
});

