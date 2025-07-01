document.addEventListener("DOMContentLoaded", function () {
    // Abre modal para adicionar meta
    window.abrirModalMeta = function () {
        document.getElementById("modalMeta").style.display = "block";
    };

    // Fecha modal de adicionar meta
    window.fecharModalMeta = function () {
        document.getElementById("modalMeta").style.display = "none";
    };


    // Abre modal para adicionar valor
    window.abrirModalValorMeta = function (button) {
        const metaId = button.getAttribute("data-meta-id");
        const modal = document.getElementById("modal-valor-meta");
        modal.setAttribute("data-meta-id", metaId);
        modal.style.display = "block";
    };

    // Fecha modal de adicionar valor
    window.fecharModalValorMeta = function () {
        document.getElementById("modal-valor-meta").style.display = "none";
    };

    // Enviar valor para a meta via AJAX
    document.getElementById("form-valor-meta").addEventListener("submit", function (e) {
        e.preventDefault();

        const metaId = document.getElementById("modal-valor-meta").getAttribute("data-meta-id");
        const valorMeta = document.getElementById("input-valor-meta").value;

        fetch(`/metas/atualizar/${metaId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ valor_meta: valorMeta }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert("Meta atualizada com sucesso!");
                    location.reload();
                } else {
                    alert("Erro ao atualizar a meta: " + data.error);
                }
            })
            .catch((error) => alert("Erro ao processar a solicitação."));
    });

    // Excluir meta
    document.querySelectorAll(".excluir-transacao").forEach((button) => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const metaId = this.getAttribute("data-id");

            if (confirm("Deseja realmente excluir esta meta?")) {
                fetch(`/metas/excluir/${metaId}/`, {
                    method: "POST",
                    headers: { "X-CSRFToken": getCSRFToken() },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.success) {
                            alert("Meta excluída com sucesso!");
                            location.reload();
                        } else {
                            alert("Erro ao excluir a meta.");
                        }
                    });
            }
        });
    });

    // Obter CSRF Token
    function getCSRFToken() {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split("=");
            if (name === "csrftoken") return value;
        }
        return null;
    }
});

function toggleMenu(element) {
    const menu = element.nextElementSibling; // Obtém o próximo elemento irmão (o menu)
    const menusAtivos = document.querySelectorAll(".menu");

    // Fecha outros menus abertos
    menusAtivos.forEach((ativo) => {
        if (ativo !== menu) {
            ativo.style.display = "none";
        }
    });

    // Alterna a exibição do menu atual
    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }
}

// Fecha o menu ao clicar fora
document.addEventListener("click", function (e) {
    const isDots = e.target.closest(".dots");
    const isMenu = e.target.closest(".menu");

    if (!isDots && !isMenu) {
        document.querySelectorAll(".menu").forEach((menu) => {
            menu.style.display = "none";
        });
    }
});

function atualizarProgresso(meta_id, valor_atual, valor_meta) {
    if (valor_meta === 0) {
        console.error("O valor da meta não pode ser 0.");
        return;
    }
    let porcentagem = (valor_atual / valor_meta) * 100;
    porcentagem = Math.min(Math.max(porcentagem, 0), 100);
    const barraProgresso = document.querySelector(`#barra-progresso-${meta_id} .progresso`);
    barraProgresso.style.width = `${porcentagem}%`;
}

document.addEventListener("DOMContentLoaded", function () {
    const metas = [
        {
            id: 1,
            valor_atual: parseFloat(document.querySelector("#meta-1-valor-atual").textContent.replace('R$', '').trim()),
            valor_meta: parseFloat(document.querySelector("#meta-1-valor-meta").textContent.replace('R$', '').trim()),
        },
        {
            id: 2,
            valor_atual: parseFloat(document.querySelector("#meta-2-valor-atual").textContent.replace('R$', '').trim()),
            valor_meta: parseFloat(document.querySelector("#meta-2-valor-meta").textContent.replace('R$', '').trim()),
        },
    ];

    metas.forEach((meta) => {
        atualizarProgresso(meta.id, meta.valor_atual, meta.valor_meta);
    });
});