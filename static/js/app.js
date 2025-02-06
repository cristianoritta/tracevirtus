$(document).ready(function () {

    $('body').on('click', '.show-modal', function (e) {
        e.preventDefault();

        $.ajax({
            url: $(this).attr('href'),
            type: 'GET',
            dataType: 'html',
            beforeSend: function () {
                $("#modal-body").html("<span class='text-white'><i class='fas fa-spinner fa-spin fa-3x fa-fw margin-bottom'></i> carregando...</span>");
                $('#open-modal').trigger('click');
            },
            success: function (html) {
                $("#modal-body").html(html);

            },
            error: function (xhr) {
                $('#modal').modal('hide');
                $("#modal-body").html('');

                Swal.fire({
                    title: 'WTK',
                    text: "Desculpe, não foi possível executar a ação.\n\n" + xhr.responseText,
                    type: 'error',
                    icon: 'info',
                });
            }
        });
        $("#modal-body").html("<span class='text-white'><i class='fas fa-spinner fa-spin fa-fw margin-bottom'></i> carregando...</span>");
    });

    $('body').on('submit', '.modal-form', function (e) {
        e.preventDefault();

        data = $(this).serialize();
        $.post($(this).attr('action'), data);
        $('.modal__close').trigger('click');

    });

    $('body').on('click', '.ajaxGlobalDbRowToForm', function (e) {
        e.preventDefault();
        form = $(this).data('form');
        callback = $(this).attr('callback');
        buttonContent = $(this).html();
        button = $(this);

        $.ajax({
            url: $(this).attr('href'),
            type: 'GET',
            dataType: 'json',
            beforeSend: function () {
                button.html("<i class='fa fa-spinner fa-spin fa-fw'></i>");
                if ($(this).attr('callbefore') != undefined) {
                    eval($(this).attr('callbefore'))();
                }
            },
            success: function (response) {
                $.populateForm('#' + form, response);
            },
            error: function (xhr) {
                Swal.fire({
                    title: 'MTK',
                    text: xhr.responseText,
                    type: 'danger',
                    icon: 'error',
                });
            },
            complete: function () {
                button.html(buttonContent);
                if (callback != undefined) {
                    eval(callback)();
                }
            }
        });
    });

    $('body').on('click', '.ajaxGlobalDelete', function (e) {
        e.preventDefault();

        Swal.fire({
            title: 'Excluir',
            text: 'Deseja excluir esse registro ?',
            type: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sim',
            cancelButtonText: 'Não'
        }).then((result) => {
            if (result.value == true) {
                buttonContent = $(this).html();
                button = $(this);

                $.ajax({
                    url: $(this).attr('href'),
                    type: 'get',
                    dataType: 'json',
                    beforeSend: function () {
                        button.html("<i class='fa fa-spinner fa-spin fa-fw'></i>");
                    },
                    success: function (response) {
                        button.html(buttonContent);

                        if (response.status == 'redirect') {
                            Swal.fire({
                                title: 'TraceVirtus',
                                text: response.message,
                                type: 'success',
                                icon: 'success',
                            });
                            window.location.replace(response.href);
                        } else if (response.status == true) {
                            if (response.message) {
                                Swal.fire({
                                    title: 'TraceVirtus',
                                    text: response.message,
                                    type: 'success',
                                    icon: 'success',
                                });
                            }
                            if (button.attr('callback') != undefined) {
                                var call = button.attr('callback');
                                eval(call)(button, response);
                            }
                        } else {
                            Swal.fire({
                                title: 'TraceVirtus',
                                text: response.message,
                                type: 'danger',
                                icon: 'info',
                            });
                        }
                    },
                    error: function (xhr) {
                        button.html(buttonContent);
                        Swal.fire({
                            title: 'TraceVirtus',
                            text: xhr.responseText,
                            type: 'danger',
                            icon: 'info',
                        });
                    }
                });
            }
        });
    });

    $('#btn-submit').click(function () {
        $(this).html("<i class='fa fa-spinner fa-spin fa-fw'></i> Enviar");
    });

    $("select").each(function () {
        if ($(this).attr('value')) {
            $(this).val($(this).attr('value'));
        }
    });

    setTimeout(function () {
        if ($('.alert').length > 0) {
            $('.alert').hide('slow');
        }
    }, 3000);
});

/** Preenche um formulario */
jQuery.populateForm = function (form, values, ignoreList) {
    if (ignoreList === undefined) {
        ignoreList = [];
    }

    $(form + " input, " + form + " select, " + form + " textarea").each(function () {
        if (ignoreList.indexOf($(this).attr('name')) < 0) {
            if (values[$(this).attr('name')]) {
                $(this).val(values[$(this).attr('name')]);
            }
        }
        $.adjustSelect();
    });
};

jQuery.adjustSelect = function () {
    $("select").each(function () {
        if ($(this).attr('value')) {
            $(this).val($(this).attr('value'));
        }
    });
}
