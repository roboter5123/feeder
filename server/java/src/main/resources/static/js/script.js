$(document).ready(function () {

    let curScreen = $("#mainScreen")
    let feeders
    let schedule

    init()

    function init() {

        if (document.cookie.length < 1 || checkCookie()) {

            window.location.replace("/login")
            return
        }

        getFeeders()
        setupFeederSelects()
    }

    function checkCookie() {

        let token = document.cookie.substring(6)
        let cookieValidity = false;
        let data = {"token": token}

        $.ajax({
            "async": false,
            "url": "/api/checkCookie",
            "type": "POST",
            "contentType": "application/json;",
            "data": JSON.stringify(data),
            "success": function (result) {

                result = JSON.parse(result)
                console.log(result)
                cookieValidity = result["success"]

                if (cookieValidity === false) {

                    document.cookie = "login= ; expires = Thu, 01 Jan 1970 00:00:00 GMT"
                }
            }
        })

        return !cookieValidity
    }


    function getFeeders() {

        let token = document.cookie.substring(6)
        let data = {"token": token}

        $.ajax({
            "async": false,
            "url": "/api/getFeeders",
            "type": "POST",
            "contentType": "application/json;",
            "data": JSON.stringify(data),
            "success": function (result) {
                extractFeeders(result)
            }
        })
    }

    function setupFeederSelects() {

        let selects = $(".feederSelect")

        for (let i = 0; i < selects.length; i++) {

            Object.keys(feeders).forEach(function (key) {

                let feeder = $("<option></option>").text(key)
                feeder.attr("value", feeders[key])
                $(selects[i]).append(feeder)
            })
        }
    }

    $(".sidebarElement").click(function () {

        let data = $(this).attr("id")

        if (data === "burger") {

            burger()
            return

        } else if (data === "schedule") {

            setupSchedule($("#scheduleSelect").val())
        }

        curScreen.toggleClass("active")
        curScreen = $("#" + data + "Screen")
        curScreen.toggleClass("active")

    })

    function burger() {

        $("#sidebar").toggleClass("active")
    }

    function setupSchedule(uuid = undefined) {

        if (uuid !== undefined) {

            let token = document.cookie.substring(6)
            let data = {"token": token, "uuid": uuid}

            $.ajax({
                "async": false,
                "url": "/api/getSchedule",
                "type": "POST",
                "contentType": "application/json;",
                "data": JSON.stringify(data),
                "success": function (result) {

                    result = JSON.parse(result)
                    schedule = result["schedule"]
                    Object.keys(schedule).forEach(function (key) {

                        schedule[key] = JSON.parse(result["schedule"][key])
                    })
                }
            })
        }

        let days = $(".weekday")

        for (let i = 0; i < days.length; i++) {

            let day = $(days[i]).attr("id")
            $(days[i]).find(".dayTasks").empty();
            let currentSchedule = schedule[day]

            if (currentSchedule.length === 0) {

                continue
            }

            Object.keys(currentSchedule).forEach(function (key) {

                let element = $("<div></div>")

                let time = $('<input type="time" class="scheduleTime"/>').val(key)
                time.attr("data-time", key)
                time.change(function () {
                    updateTime(this, day)
                })

                let amount = $('<input type="number" class="scheduleAmount" min = "0"/>').val(currentSchedule[key])
                amount.change(function (){

                    updateAmount(this, day)
                })
                element.append(time)
                element.append(amount)
                $(days[i]).find(".dayTasks").append(element)
            })
        }
    }

    function updateAmount(element, day) {

        let time = $(element).siblings("input[type='time']").attr("data-time")
        schedule[day][time] = parseInt($(element).val())
        console.log(schedule)

    }

    function updateTime(element, day) {

        let time = $(element).val()
        let oldTime = $(element).attr("data-time")

        if (schedule[day][time] === undefined) {

            schedule[day][time] = schedule[day][oldTime]

        } else {

            schedule[day][time] = schedule[day][oldTime]
        }

        delete schedule[day][oldTime]

        setupSchedule()
    }

    $("#scheduleSelect").change(function () {

        setupSchedule($(this).val())
    })

    $("#feedButton").click(function () {


        let token = document.cookie.substring(6)
        let amount = $("#dispenseAmount").val()
        let uuid = $("#dispenseSelect").val()

        let data = {"token": token, "uuid": uuid, "args": '{"amount": ' + amount + '}'}

        $.ajax({
            "async": false,
            "url": "/api/dispense",
            "type": "POST",
            "contentType": "application/json;",
            "data": JSON.stringify(data),
            "success": function (result) {
            }
        })

    })

    function extractFeeders(result) {

        feeders = JSON.parse(result)["uuids"]
    }


})