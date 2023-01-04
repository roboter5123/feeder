$(document).ready(function(){

    let curScreen = loginScreen;
    
    $("#login input[type = 'submit']").click(function(e){

        e.preventDefault();

        let data = "{ 'email': '"
        let email = $("#email").text()
        data += email + "', 'password':'"
        let password = md5$("#passwordl").text()


    })
})