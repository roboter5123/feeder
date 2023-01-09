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


    })

    function login(result){

        if (result["success"] !== true){

            console.log("Failed to login retry")
            return
        }

        console.log(result)
        document.cookie =`login=${result["token"]};expires=${new Date(new Date().getTime()+24*60*60*1000).toGMTString()}`
        console.log(document.cookie)
        window.location.replace("/")
        console.log("logged in successfully")
    }

})