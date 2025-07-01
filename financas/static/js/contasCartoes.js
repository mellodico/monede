// JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const component = document.querySelector('.contas-cartoes-component');
    const expandButton = component.querySelector('.expand-button');

    expandButton.addEventListener('click', function() {
        component.classList.toggle('expanded');
    });
});