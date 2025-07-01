// Função para abrir o modal com informações da categoria
function abrirModal(nomeCategoria, corCategoria, iconeCategoria) {
    // Preencher os dados da categoria no modal
    document.getElementById('modal-nome-categoria').innerText = nomeCategoria;
    document.getElementById('modal-icone-categoria').innerHTML = `<i class="${iconeCategoria}" style="background-color: ${corCategoria};"></i>`;
    document.getElementById('input-nome-categoria').value = nomeCategoria;

    // Exibir o modal
    document.getElementById('modalCategoriaInfo').style.display = 'block';
}

// Função para fechar o modal
function fecharModal() {
    // Ocultar o modal
    document.getElementById('modalCategoriaInfo').style.display = 'none';
}

// Configuração do slider
document.getElementById('valor-slider').addEventListener('input', function() {
    document.getElementById('valor').value = this.value;
});
