/**
 * Created by cyh on 2015/11/9.
 */

$('#submit').click(function () {
    var username = $('#user').val();
    var password = $('#pass').val();
    var publicStr = $('#publicStr').val();

    var sha_password = sha256.hex(password);

    username = cryptico.encrypt(username, publicStr).cipher;
    password = cryptico.encrypt(sha_password, publicStr).cipher;
    $.post('/ajax/login', {
        user: username,
        password: password,
        token: getCookie('token')
    }, function (data, status) {
        if (data.code == 1) {
            sessionStorage.password = sha_password;
            location.href = location.href;
        }
        else {
            alert(data.msg);
        }
    }, 'json');
});

document.onkeydown = function (e) {
    var ev = document.all ? window.event : e;
    if (ev.keyCode == 13) {
        $('#submit').click();
    }
};