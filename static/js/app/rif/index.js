$('.delete-rif').click(function (event) {
    // Captura a URL do hx-delete
    var deleteUrl = this.getAttribute('hx-delete');
    var targetElement = this.closest('tr'); // Define o alvo para remoção

    event.preventDefault(); // Corrigido para ser chamado como método

    Swal.fire({
        title: 'Tem certeza?',
        text: "Você tem certeza que deseja excluir este RIF ?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Excluir',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            // Adiciona um listener global para o evento htmx:afterRequest
            document.body.addEventListener('htmx:afterRequest', function (event) {
                console.log(event);
                // Verifica se a URL da requisição é a mesma do deleteUrl

                try {
                    var jsonResponse = JSON.parse(event.detail.xhr.responseText);
                    // Exibe o SweetAlert com a mensagem de sucesso
                    Swal.fire({
                        title: 'Excluído!',
                        text: jsonResponse.message,
                        icon: 'success',
                        confirmButtonText: 'OK'
                    }).then(() => {
                        // Remove o elemento após o SweetAlert de confirmação
                        targetElement.remove();
                    });

                    targetElement.remove();
                } catch (e) {
                    Swal.fire({
                        title: 'Erro!',
                        text: 'Não foi possível excluir o RIF.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                }
            }, { once: true }); // Garante que o listener seja chamado apenas uma vez

            // Executa a requisição DELETE manualmente usando htmx.ajax
            htmx.ajax('DELETE', deleteUrl, { target: targetElement });
        }
    });
});
