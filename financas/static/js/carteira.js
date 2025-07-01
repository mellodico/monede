function abrirModalConta() {
  document.getElementById('modalConta').style.display = 'flex';
}

function fecharModalConta() {
  document.getElementById('modalConta').style.display = 'none';
}

function abrirModalBanco() {
  document.getElementById('modalCriarBanco').style.display = 'flex';
}

function fecharModalBanco() {
  document.getElementById('modalCriarBanco').style.display = 'none';
}

// Fechar o modal ao clicar fora do conteúdo
window.onclick = function(event) {
  const modalConta = document.getElementById('modalConta');
  const modalBanco = document.getElementById('modalCriarBanco');
  if (event.target === modalConta) {
      modalConta.style.display = 'none';
  }
  if (event.target === modalBanco) {
      modalBanco.style.display = 'none';
  }
};

document.addEventListener('DOMContentLoaded', function() {
  const novaContaButton = document.querySelector('#novaContaButton');
  const novaContaModal = new bootstrap.Modal(document.getElementById('novaContaModal'));

  if (novaContaButton) {
      novaContaButton.addEventListener('click', function() {
          novaContaModal.show();
      });
  }

  const novoCartaoButton = document.querySelector('#novoCartaoButton');
  const novoCartaoModal = new bootstrap.Modal(document.getElementById('novoCartaoModal'));

  if (novoCartaoButton) {
      novoCartaoButton.addEventListener('click', function() {
          novoCartaoModal.show();
      });
  }
});