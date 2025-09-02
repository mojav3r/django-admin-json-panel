$(document).ready(function () {
    $('#datatable .main-row').on('click', function () {
        var parentId = $(this).data('id');
        var $detailsRow = $('#datatable .details-row[data-parent-id="' + parentId + '"]');

        if ($(this).hasClass('t-active')) {
            $detailsRow.slideUp('fast', function () {
                $(this).prev('.main-row').removeClass('t-active t-selected');
            });
        } else {
            $('#datatable .details-row').slideUp('fast');
            $('#datatable .main-row').removeClass('t-active t-selected');

            $(this).addClass('t-active');
            $detailsRow.slideDown('fast', function () {
                if ($detailsRow.prev('.main-row').find('.row-checkbox').is(':checked')) {
                    $detailsRow.prev('.main-row').addClass('t-selected');
                }
            });
        }
    });

    $('#datatable .row-checkbox').on('click', function (e) {
        e.stopPropagation();
    });

    $('#select-all, #select-all-footer').on('click', function () {
        var isChecked = $(this).is(':checked');
        $('#datatable .row-checkbox').prop('checked', isChecked).trigger('change');
    });

    $('#datatable .row-checkbox').on('change', function () {
        var $row = $(this).closest('tr');
        if ($(this).is(':checked')) {
            $row.addClass('t-selected');
            handleCheckboxClick(this)
        } else {
            $row.removeClass('t-selected');
            handleCheckboxClick(this)

        }

        var allChecked = $('#datatable .row-checkbox').length === $('#datatable .row-checkbox:checked').length;
        $('#select-all, #select-all-footer').prop('checked', allChecked);
    });
});

// Get the tags and input elements from the DOM
const tags = document.getElementById('tags');
const input = document.getElementById('input-tag');

function addTags(text) {
    event.preventDefault();
    let tagContent = null;
    if (text) {
        tagContent = text;
    } else {
        tagContent = input.value.trim();
    }
    var parts = tagContent.split(":");
    if (parts.length !== 1 && tagContent.slice(-1) !== ":") {
        const tagList = document.getElementById('tags');
        const buttons = tagList.getElementsByClassName('btn btn-outline-primary rounded-pill mt-2 delete-button');
        let exists = false;
        for (let i = 0; i < buttons.length; i++) {
            if (buttons[i].innerText.includes(tagContent.toLowerCase().split(':')[0])) {
                exists = true;
                break;
            }
        }
        if (!exists) {
            // Create a new button element for the tag
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn btn-outline-primary rounded-pill mt-2 delete-button';
            button.style.display = 'flex';

            // If the trimmed value is not an empty string
            if (tagContent !== '') {
                // Set the text content of the button to the trimmed value
                button.innerText = tagContent;
                const searchField = document.getElementById('searchbar')
                if (!searchField.value.includes(tagContent)) {
                    if (searchField.value) {
                        searchField.value += '&&'
                        searchField.value += tagContent
                    } else {
                        searchField.value += tagContent
                    }
                }
            }

            // Add a delete button inside the main button
            const deleteButton = document.createElement('i');
            deleteButton.className = 'ri-close-line text-secondary';
            deleteButton.style.marginLeft = '5px';
            deleteButton.addEventListener('click', function () {
                tagList.removeChild(button);
                const searchField = document.getElementById('searchbar');
                const value = tagContent;
                const text = searchField.value.replace(value, '');
                let textFormat = text.replace(/^&&|&&$/g, '');
                let t = textFormat.replace('&&&&', '&&');
                searchField.value = t;
            });

            button.appendChild(deleteButton);

            // Append the button to the tags list
            tagList.appendChild(button);

            // Clear the input element's value
            input.value = '';
        }
    }
}

input.addEventListener('keydown', function (event) {
    // Check if the key pressed is 'Enter'
    if (event.key === 'Enter') {
        addTags();
    }
});

function indexUpdateInput(value) {
    const input = document.getElementById('input-tag');
    const tagList = document.getElementById('tags');
    const buttons = tagList.getElementsByClassName('btn btn-outline-primary rounded-pill mt-2 delete-button');
    let exists = false;
    for (let i = 0; i < buttons.length; i++) {
        if (buttons[i].innerText.includes(value)) {
            exists = true;
            break;
        }
    }
    if (!exists) {
        if (input.value.includes(':')) {
            addTags();
            document.getElementById('input-tag').value = "";
            document.getElementById('input-tag').value += value;
            document.getElementById('input-tag').focus();
        } else {
            document.getElementById('input-tag').value = "";
            document.getElementById('input-tag').value += value;
            document.getElementById('input-tag').focus();
        }
    }
}

window.addEventListener('load', (event) => {
    const input = document.getElementById('input-tag');
    const text = input.value;
    const words = text.split("&&");
    for (let word of words) {
        addTags(word);
    }
});

window.addEventListener('load', (event) => {
    const input = document.getElementById('searchbar');
    const text = input.value;
    const words = text.split("&&");
    for (let word of words) {
        addTags(word);
    }
});


// $(document).ready(function () {
//     $('#go-button').on('click', function () {
//         $('#datatable .row-checkbox').prop('checked', false);
//         $('#datatable .row-checkbox').trigger('change');
//     });
// });

function handleCheckboxClick(checkbox) {
    const hiddenInput = document.getElementById('ids');
    const selectedValue = checkbox.value;
    let selectedIds = hiddenInput.value ? JSON.parse(hiddenInput.value) : [];

    // If the checkbox is checked, add its value to the list
    if (checkbox.checked) {
        selectedIds.push(selectedValue);
    } else { // If the checkbox is unchecked, remove its value from the list
        const index = selectedIds.indexOf(selectedValue);
        if (index !== -1) {
            selectedIds.splice(index, 1);
        }
    }

    // Update the value of the hidden input with the updated list of selected ids
    hiddenInput.value = JSON.stringify(selectedIds);
}
