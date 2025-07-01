document.addEventListener("DOMContentLoaded", function() {
  console.log("JavaScript carregado!");

  // Elementos DOM
  const dateInputInicial = document.getElementById("data-inicial");
  const dateInputFinal = document.getElementById("data-final");
  const dateTextInicial = document.getElementById("dataInicialText");
  const dateTextFinal = document.getElementById("dataFinalText");
  const perfilMenu = document.getElementById('perfilMenu');
  const contasCartoesConteudo = document.getElementById('conteudoContasCartoes');
  const iconeExpandir = document.getElementById('iconeExpandir');

  // Funções para Data Inicial
  function toggleDatePicker() {
    dateTextInicial.style.display = "none";
    dateInputInicial.style.display = "inline";
    dateInputInicial.focus();
  }

  function updateDateText() {
    if (dateInputInicial.value) {
      const selectedDate = new Date(dateInputInicial.value);
      const formattedDate = selectedDate.toLocaleDateString("pt-BR", {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
      dateTextInicial.textContent = formattedDate;
      dateInputInicial.style.display = "none";
      dateTextInicial.style.display = "inline";
    }
  }

  // Funções para Data Final
  function toggleDatePickerFinal() {
    dateTextFinal.style.display = "none";
    dateInputFinal.style.display = "inline";
    dateInputFinal.focus();
  }

  function updateDateFinalText() {
    if (dateInputFinal.value) {
      const selectedDate = new Date(dateInputFinal.value);
      const formattedDate = selectedDate.toLocaleDateString("pt-BR", {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
      dateTextFinal.textContent = formattedDate;
      dateInputFinal.style.display = "none";
      dateTextFinal.style.display = "inline";
    }
  }

  // Funções do Dropdown
  function toggleDropdown() {
    const dropdownContent = document.getElementById("dropdownContent");
    dropdownContent.style.display = dropdownContent.style.display === "block" ? "none" : "block";
  }

  // Função para o Menu de Perfil
  function togglePerfilMenu() {
    perfilMenu.classList.toggle('ativo');
  }

  // Função para Contas e Cartões
  function toggleContasCartoes() {
    contasCartoesConteudo.classList.toggle('ativo');
    iconeExpandir.textContent = contasCartoesConteudo.classList.contains('ativo') ? '▼' : '▲';
  }

  // Função para mostrar balanço
  function mostrarBalanco() {
    console.log('Mostrar balanço');
  }

  // Função para formatação de moeda
  function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  }

  // Funções para o modal de nova transação
  function abrirModalNovaTransacao() {
    const modal = document.getElementById("novaTransacaoModal");
    modal.style.display = "block";
  }

  function fecharModalNovaTransacao() {
    const modal = document.getElementById("novaTransacaoModal");
    modal.style.display = "none";
  }

  // Funções de filtros
  function aplicarFiltro(filtro) {
    const filtrosSelecionados = document.getElementById("filtrosSelecionados");

    // Criar o elemento do filtro selecionado
    const filtroElement = document.createElement("div");
    filtroElement.classList.add("filtro-selecionado");
    filtroElement.textContent = filtro;
    filtroElement.onclick = () => removerFiltro(filtroElement);

    // Adicionar o ícone de fechar
    const iconeFechar = document.createElement("img");
    iconeFechar.src = "{% static 'icons/close.svg' %}";
    iconeFechar.alt = "Fechar";
    filtroElement.appendChild(iconeFechar);

    // Adicionar o filtro selecionado à lista
    filtrosSelecionados.appendChild(filtroElement);

    // Redirecionar para o frame 209
    window.location.hash = "frame-209";
  }

  function removerFiltro(filtroElement) {
    filtroElement.remove();
    // Adicione aqui a lógica para atualizar a tabela com os novos filtros
  }

  // Event Listeners
  if (dateInputInicial) {
    dateInputInicial.addEventListener("change", updateDateText);
  }

  if (dateInputFinal) {
    dateInputFinal.addEventListener("change", updateDateFinalText);
  }

  // Listener para fechar dropdown ao clicar fora
  window.addEventListener('click', function(event) {
    if (!event.target.closest('.dropdown')) {
      const dropdownContent = document.getElementById("dropdownContent");
      if (dropdownContent) {
        dropdownContent.style.display = "none";
      }
    }

    // Fechar menu de perfil ao clicar fora
    if (!event.target.closest('.perfil-container')) {
      perfilMenu?.classList.remove('ativo');
    }
  });

  // Expor funções globalmente, caso necessário
  window.toggleDatePicker = toggleDatePicker;
  window.updateDateText = updateDateText;
  window.toggleDatePickerFinal = toggleDatePickerFinal;
  window.updateDateFinalText = updateDateFinalText;
  window.mostrarBalanco = mostrarBalanco;
  window.abrirModalNovaTransacao = abrirModalNovaTransacao;
  window.fecharModalNovaTransacao = fecharModalNovaTransacao;
  window.toggleDropdown = toggleDropdown;
  window.aplicarFiltro = aplicarFiltro;
  window.removerFiltro = removerFiltro;
});
