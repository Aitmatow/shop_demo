function setFormId(form, formsNumber) {
    let formId = 'order_products-' + formsNumber;
    let oldId = form.prop('id');
    form.prop('id', formId);

    let fields = ['product', 'amount', 'id', 'DELETE'];
    fields.forEach(function(field) {
        let element = form.find('#id_' + oldId + '-' + field);
        let fieldName = formId + '-' + field;
        element.prop('name', fieldName);
        element.prop('id', 'id_' + fieldName);
    });

    let deleteButton = form.find('.btn-danger');
    deleteButton.data('id', formId);
}

function formReset(form) {
    let formId = form.prop('id');
    form.removeClass('d-none');

    let fields = ['product', 'amount', 'id'];
    fields.forEach(function(field) {
        let element = form.find('#id_' + formId + '-' + field);
        element.val('');
    });

    let deleteCheckbox = form.find('#id_' + formId + '-' + 'DELETE');
    deleteCheckbox.prop('checked', false);

    let errors = form.find('.text-danger');
    errors.remove();

    let deleteButton = form.find('.btn-danger');
    deleteButton.off('click');
    deleteButton.click(deleteProductForm);
}

function addProductForm (event) {
    let totalFormsInput = $("#id_order_products-TOTAL_FORMS");
    let maxFormsInput = $("#id_order_products-MAX_NUM_FORMS");
    let totalForms = totalFormsInput.val();
    let maxForms = maxFormsInput.val();
    if(totalForms === maxForms) {
        alert('Максимальное количество товаров добавлено!');
    } else {
        let newForm =$("#product_forms .form-row").first().clone();
        setFormId(newForm, totalForms);
        formReset(newForm);
        $("#product_forms").append(newForm);
        totalFormsInput.val(parseInt(totalForms) + 1);
    }
}

function deleteProductForm(event) {
    let totalFormsInput = $("#id_order_products-TOTAL_FORMS");
    let minFormsInput = $("#id_order_products-MIN_NUM_FORMS");
    let totalForms = totalFormsInput.val();
    let minForms = minFormsInput.val();
    if(totalForms === minForms) {
        alert('В заказе должно быть хотя бы ' + minForms + " товар(а/ов).");
    } else {
        let formId = $(event.target).data('id');
        let form = $("#" + formId);

        let idInput = form.find('#id_' + formId + '-id');
        if (idInput.val()) {
            let deleteCheckbox = form.find('#id_' + formId + '-DELETE');
            form.addClass('d-none');
            deleteCheckbox.prop('checked', true);
        } else {
            form.remove();
            totalFormsInput.val(parseInt(totalForms) - 1);
        }

        let forms = $("#product_forms .form-row");
        for(let i = 0; i < forms.length; i++) {
            setFormId($(forms[i]), i);
        }
    }
}

$(document).ready(function() {
    $('#add_product_form').click(addProductForm);
    $('#product_forms button.btn-danger').click(deleteProductForm)
});