// static/js/subcategorias.js
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalSubcategoria');
    const botaoCriar = document.getElementById('botaoCriarSubcategoria');
    const campoCor = document.querySelector('input[name="cor"]');
    const campoIcone = document.querySelector('input[name="icone"]');
    
    // Abrir modal
    botaoCriar.addEventListener('click', function() {
        modal.style.display = 'block';
    });
    
    // Fechar modal ao clicar fora
    window.addEventListener('click', function(evento) {
        if (evento.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Funcionalidade do seletor de cor
    const opcoesCor = document.querySelectorAll('.opcao-cor');
    opcoesCor.forEach(opcao => {
        const cor = opcao.dataset.cor;
        opcao.style.backgroundColor = cor;
        
        opcao.addEventListener('click', function() {
            campoCor.value = cor;
            // Remove a classe selecionada de todas as opções
            opcoesCor.forEach(opt => opt.classList.remove('selecionada'));
            // Adiciona a classe selecionada à opção clicada
            opcao.classList.add('selecionada');
        });
    });
    
    // Funcionalidade do seletor de ícone
    const opcoesIcone = document.querySelectorAll('.opcao-icone');
    opcoesIcone.forEach(opcao => {
        const icone = opcao.dataset.icone;
        opcao.innerHTML = `<i class="${icone}"></i>`;
        
        opcao.addEventListener('click', function() {
            campoIcone.value = icone;
            // Remove a classe selecionada de todas as opções
            opcoesIcone.forEach(opt => opt.classList.remove('selecionada'));
            // Adiciona a classe selecionada à opção clicada
            opcao.classList.add('selecionada');
        });
    });
});
