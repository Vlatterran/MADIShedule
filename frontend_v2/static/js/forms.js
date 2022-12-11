const overlay = $('#overlay-modal');

const modalElem = $('.modal[data-modal="1"]');
const closeButton = $('.modal__cross');

closeButton.click(function (_) {
    modalElem.removeClass('active');
    overlay.removeClass('active');
});
const open_form = (e) => {
    console.log(e);
    const {item} = e.detail
    modalElem.addClass('active');
    overlay.addClass('active');
    $('#start>input')[0].value = item.start;
    $('#end>input')[0].value = item.end;
    const classroomInput = $('#classroom>input');
    classroomInput.prop("readonly", false);
    classroomInput[0].value = item.date;
    classroomInput.prop("readonly", true);
}

$('.submit').click((e) => {
    e.preventDefault()
    const data = $('form').serializeArray().reduce(function (obj, item) {
        obj[item.name] = item.value;
        return obj;
    }, {});
    console.log(data)
    // TODO: format data for server specifications
    $.ajax("http://localhost:8008/schedule/create_non_periodic", {
        method: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: console.log
    })
})

