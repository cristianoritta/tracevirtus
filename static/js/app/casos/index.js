
// Função para ativar o caso e alterar as classes dos botões
function ativarCaso(casoId) {
    // Remove 'text-warning' de todos os botões
    document.querySelectorAll('button[id^="caso-btn-"]').forEach(function (btn) {
        btn.classList.remove('text-warning');
    });

    // Adiciona 'text-warning' ao botão do caso ativado
    const activeBtn = document.getElementById('caso-btn-' + casoId);
    if (activeBtn) {
        activeBtn.classList.add('text-warning');
    }
}
