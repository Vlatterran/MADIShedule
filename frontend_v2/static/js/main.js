const ts = document.querySelector('.table-schedule')

$.ajax("http://localhost:8008/classrooms", {
    method: "GET",
    success: create
})

var TS = null;

function create(data) {


    TS = new TableSchedule(ts, {
        dayStart: 8,
        dayEnd: 22,
        gap: 30,
        createThreshold: 5,
        listForCols: data.sort(),
        dateFormat: (date) => date,
        extraDataset: {'id': 'id', 'type': 'type'}
    })

    ts.addEventListener('create', open_form)
    ts.addEventListener('modify', function (e) {
        const {item, coords, mod} = e.detail
        // if you don't need a form to modify other information
        const modified = Object.assign({}, item, mod);
        ts.updateEvent(coords, modified)
        // else you still need to provide a form for input
    })
    ts.addEventListener('remove', function (e) {
        const {coords} = e.detail
        ts.deleteEvent(coords)
    })

    $.ajax(`http://localhost:8008/schedule/get_by_date?date=${date_for_schedule}`, {
        method: "GET",
        headers: {
            'Access-Control-Allow-Origin': '*',
        },
        success: (data) => {
            data.forEach(addEvent)
        }
    })
}

const addEvent = (e) => {
    TS.addEvent({
        date: e.classroom_id,
        start: e.start_time.slice(0, 5),
        end: e.end_time.slice(0, 5),
        title: e.name,
        id: e.id,
        type: e.type,
    })
}