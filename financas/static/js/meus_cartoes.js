// Função para abrir o modal de cartão
function abrirModalCartao() {
    const modal = document.getElementById('modalCartao');
    modal.style.display = 'block';
}

// Função para abrir o modal de conta
function abrirModalConta() {
    const modal = document.getElementById('modalConta');
    modal.style.display = 'block';
}

// Função genérica para fechar um modal pelo ID
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Evento para fechar o modal ao clicar fora dele
window.onclick = function (event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach((modal) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
};

// Função placeholder para fechar fatura de um cartão
function fecharFatura(cartaoId) {
    // Implementar a lógica para fechar a fatura no backend
    console.log('Fechando fatura do cartão com ID:', cartaoId);
}
