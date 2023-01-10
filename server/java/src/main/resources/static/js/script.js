$(document).ready(function () {

    let curScreen = $("#mainScreen")
    let feeders

    init()

    function init() {

        if (document.cookie.length < 1 || checkCookie()) {

            window.location.replace("/login")
            return
        }

        getFeeders()
        setupFeederSelects()
    }

    function checkCookie(){

        let token = document.cookie.substring(6)
        let cookieValidity = false;
        data = {"token": token}

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

                if (cookieValidity === false){

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

        }else if(data === "schedule"){

            setupSchedule($("#scheduleSelect").val())
        }

        curScreen.toggleClass("active")
        curScreen = $("#" + data + "Screen")
        curScreen.toggleClass("active")

    })

    function burger() {

        $("#sidebar").toggleClass("active")
    }

    function setupSchedule(uuid){

        let token = document.cookie.substring(6)
        let data = {"token": token, "uuid": uuid}

        $.ajax({
            "async": false,
            "url": "/api/getSchedule",
            "type": "POST",
            "contentType": "application/json;",
            "data": JSON.stringify(data),
            "success": function (result){

                console.log(result)
                result = result.split("\\").join("")
                console.log(result)
                result= "{" + result.split('{\"').join("")
                console.log(result)
                result = JSON.parse(result)
                console.log(result)

            }
        })
    }

    $("#feedButton").click(function () {

        console.log(document.cookie.substring(6))
        let token = document.cookie.substring(6)
        let amount = $("#dispenseAmount").val()
        let uuid = $("#dispenseSelect").val()
        data = {"token": token, "uuid": uuid, "args": '{"amount": ' + amount + '}'}
        console.log(data)
        console.log(JSON.stringify(data))

        $.ajax({
            "async": false,
            "url": "/api/dispense",
            "type": "POST",
            "contentType": "application/json;",
            "data": JSON.stringify(data),
            "success": function (result) {
                console.log(result)
            }
        })

    })

    function extractFeeders(result) {

        feeders = JSON.parse(result)["uuids"]
    }


})