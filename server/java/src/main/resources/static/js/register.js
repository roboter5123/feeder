$(document).ready(function () {

    $("#register input[type = 'submit']").click(function (e) {

        e.preventDefault();

        let email = $("#email").val()
        let password = $("#password").val()

        let data = {"email": email, "password": password}
        console.log(data)

        $.ajax({
            "async": false,
            "url": "/api/register",
            "type": "POST",
            "contentType": "application/json;",
            "data": JSON.stringify(data),
            "success": function (result) {
                register(JSON.parse(result))
            }
        })

        console.log("done")

    })

    function register(result) {

        console.log(result)
        if (result["success"] !== true) {

            console.log("Failed to register retry")
            return
        }

        window.location.replace("/login")
    }
})