import os
import django

# Configurar o ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monede_project.settings')
django.setup()

from financas.models import Categoria  # Substitua 'financas' pelo nome do seu app

def populate_categories():
    categorias = [
        {"nome": "Alimentação", "cor": "#008000", "icone": "icons/categorias/alimentação.svg"},
        {"nome": "Compras", "cor": "#FF69B4", "icone": "icons/categorias/compras.svg"},
        {"nome": "Emergências", "cor": "#FFA500", "icone": "icons/categorias/emergencias.svg"},
        {"nome": "Entretenimento Digital", "cor": "#FF69B4", "icone": "icons/categorias/entretenimento digital.svg"},
        {"nome": "Impostos e Taxas", "cor": "#FFA500", "icone": "icons/categorias/impostos e taxas.svg"},
        {"nome": "Moradia", "cor": "#8B4513", "icone": "icons/categorias/moradia.svg"},
        {"nome": "Saúde", "cor": "#FF0000", "icone": "icons/categorias/saude.svg"},
        {"nome": "Serviços Financeiros e Bancários", "cor": "#800080", "icone": "icons/categorias/serviços financeiros e bancarios.svg"},
        {"nome": "Streaming", "cor": "#8B0000", "icone": "icons/categorias/streaming.svg"},
        {"nome": "Transferências e Pagamentos", "cor": "#00008B", "icone": "icons/categorias/transferencias e pagamentos.svg"},
        {"nome": "Transporte", "cor": "#6B8E23", "icone": "icons/categorias/transporte.svg"},
        {"nome": "Viagem", "cor": "#0ABAB5", "icone": "icons/categorias/viagem.svg"},
        {"nome": "Educação", "cor": "#800080", "icone": "icons/categorias/educação.svg"},
        {"nome": "Hobbies", "cor": "#40E0D0", "icone": "icons/categorias/hobbies.svg"},
        {"nome": "Investimentos", "cor": "#ADFF2F", "icone": "icons/categorias/investimento.svg"},
        {"nome": "Poupança", "cor": "#008000", "icone": "icons/categorias/poupança.svg"},
        {"nome": "Assinaturas", "cor": "#708090", "icone": "icons/categorias/assinaturas.svg"},
        {"nome": "Seguros", "cor": "#1E90FF", "icone": "icons/categorias/seguros.svg"},
        {"nome": "Empréstimos", "cor": "#808080", "icone": "icons/categorias/empréstimos.svg"},
    ]

    for categoria in categorias:
        obj, created = Categoria.objects.update_or_create(
            nome=categoria["nome"],
            defaults={
                "cor": categoria["cor"],
                "icone": categoria["icone"],
                "padrao": True,
            },
        )
        if created:
            print(f"Categoria criada: {categoria['nome']}")
        else:
            print(f"Categoria atualizada: {categoria['nome']}")

if __name__ == "__main__":
    populate_categories()
