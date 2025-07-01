// Função para abrir o modal de nova transação
function abrirModalNovaTransacao() {
  var modal = document.getElementById("modalTransacao");
  modal.style.display = "block";
}

// Função para fechar o modal de nova transação
function fecharModalTransacao() {
  var modal = document.getElementById("modalTransacao");
  modal.style.display = "none";
}

// Fechar o modal ao clicar fora dele
window.onclick = function(event) {
  var modal = document.getElementById("modalTransacao");
  if (event.target == modal) {
      modal.style.display = "none";
  }
}

// Função de busca por transações com debounce para evitar múltiplas requisições
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('#search-transactions');
  const tableBody = document.querySelector('#transactions-table tbody');
  let timeoutId;

  if (searchInput) {
      searchInput.addEventListener('input', function(e) {
          clearTimeout(timeoutId);
          
          timeoutId = setTimeout(() => {
              const searchTerm = e.target.value.trim();
              
              fetch(`/buscar-transacoes/?q=${encodeURIComponent(searchTerm)}`)
                  .then(response => response.json())
                  .then(data => {
                      if (data.error) {
                          console.error('Erro:', data.error);
                          tableBody.innerHTML = `<tr><td colspan="8">Erro ao buscar transações</td></tr>`;
                      } else {
                          tableBody.innerHTML = '';
                          data.transacoes.forEach(transacao => {
                              const row = document.createElement('tr');
                              row.classList.add('transacao-row');
                              row.innerHTML = `
                                  <td>${transacao.logo_url ? `<img src="${transacao.logo_url}" alt="Logo" class="transacao-logo">` : ''}</td>
                                  <td class="transacao-titulo">${transacao.titulo}</td>
                                  <td class="transacao-data">${transacao.data}</td>
                                  <td class="transacao-valor">${transacao.valor.toFixed(2)}</td>
                                  <td class="transacao-tipo">${transacao.tipo}</td>
                                  <td class="transacao-forma-pagamento">${transacao.forma_pagamento}</td>
                                  <td class="transacao-categoria">${transacao.categoria}</td>
                                  <td class="transacao-acoes">
                                      <a href="/editar-transacao/${transacao.id}" class="btn-editar">Editar</a>
                                      <a href="/excluir-transacao/${transacao.id}" class="btn-excluir">Excluir</a>
                                  </td>
                              `;
                              tableBody.appendChild(row);
                          });
  
                          const counter = document.querySelector('#results-counter');
                          if (counter) {
                              counter.textContent = `${data.quantidade} resultado(s) encontrado(s)`;
                          }
                      }
                  })
                  .catch(error => {
                      console.error('Erro:', error);
                      tableBody.innerHTML = `<tr><td colspan="8">Erro ao buscar transações</td></tr>`;
                  });
          }, 300); // Delay de 300ms para evitar muitas requisições
      });
  } else {
      console.error('Elemento #search-transactions não encontrado.');
  }
});

// Atualizar as opções de conta/cartão com base no tipo selecionado
function atualizarOpcoesContaCartao() {
  var tipo = document.getElementById('tipo-conta-cartao').value;
  var grupoConta = document.getElementById('grupo-conta');
  var grupoCartao = document.getElementById('grupo-cartao');

  if (tipo === 'CONTA') {
      grupoConta.style.display = 'block';
      grupoCartao.style.display = 'none';
  } else if (tipo === 'CARTAO') {
      grupoConta.style.display = 'none';
      grupoCartao.style.display = 'block';
  } else {
      grupoConta.style.display = 'none';
      grupoCartao.style.display = 'none';
  }
}

// Função para atualizar o intervalo de tempo na URL
function updateTimeRange(days) {
  window.location.href = `?time_range=${days}`;
}

// Função para alternar entre data automática e manual
function toggleDataManual(checkbox) {
  const dataInput = document.getElementById('data_transacao');

  if (checkbox.checked) {
      // Se "Definir data automaticamente" estiver marcado, preenche a data com a data atual
      const today = new Date().toISOString().split('T')[0];
      dataInput.value = today;
      dataInput.disabled = true;  // Desabilita o campo de data
  } else {
      // Se desmarcado, limpa o campo e habilita
      dataInput.value = '';  // Limpa o campo de data manualmente
      dataInput.disabled = false;
  }
}

// Caso o checkbox esteja marcado ao carregar a página, preenche a data automaticamente
document.addEventListener('DOMContentLoaded', function() {
  const checkbox = document.getElementById('automatic-date-checkbox'); // ID do checkbox de data automática
  if (checkbox && checkbox.checked) {
      toggleDataManual(checkbox);  // Chama a função de alternância de data automaticamente
  }
});


// Função para redirecionar com os filtros de data
function atualizarFiltroData() {
  // Pega os valores das datas inicial e final
  const dataInicial = document.getElementById('dataInicial').value;
  const dataFinal = document.getElementById('dataFinal').value;

  // Monta a URL com os parâmetros de data
  let url = '/transacoes/'; // A URL onde você vai filtrar as transações

  // Adiciona os parâmetros de data na URL, caso existam
  let parametros = [];
  if (dataInicial) parametros.push(`data_inicial=${dataInicial}`);
  if (dataFinal) parametros.push(`data_final=${dataFinal}`);

  if (parametros.length > 0) {
      url += '?' + parametros.join('&');
  }

  // Redireciona para a URL com os filtros
  window.location.href = url;
}

function toggleMenu(element) {
  const menu = element.nextElementSibling;
  menu.style.display = menu.style.display === "block" ? "none" : "block";
}

// Fechar o menu ao clicar fora dele
document.addEventListener('click', function(event) {
  const menus = document.querySelectorAll('.menu');
  menus.forEach(menu => {
      if (!menu.contains(event.target) && !menu.previousElementSibling.contains(event.target)) {
          menu.style.display = 'none';
      }
  });
});