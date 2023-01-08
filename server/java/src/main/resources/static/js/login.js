$(document).ready(function () {


    $("#login input[type = 'submit']").click(function (e) {

        e.preventDefault();

        let email = $("#email").val()
        let password = $("#password").val()

        let data = {"email": email, "password": password}
        console.log(data)

        $.ajax({
            "async": false,
            "url": "/api/login",
            "type": "POST",
            "contentType": "application/json;",
            "data": JSON.stringify(data),
            "success": function (result) { login(JSON.parse(result))}
        })

        console.log("done")

    })

    function login(result){

        if (result["success"] !== true){

            console.log("Failed to login retry")
            return
        }

        console.log(result)
        window.sessionStorage.setItem("token",result["token"])
        console.log("logged in successfully")
    }

})