/**
 * Created by cyh on 2015/11/27.
 */

Vue.config.delimiters = ['[[', ']]'];
var pass_form = new Vue({
        el: '#pass_form',
        data: {
            username:"",
            password:"",
            password_again:"",
            gt_id:"",
            gt_challenge:"",
            tips_text:""
        },
        methods: {
            submitClick:submitClick
        }
    }
);

var gt_captcha_obj = new window.Geetest({
    gt: pass_form.gt_id,
    challenge: pass_form.gt_challenge,
    product: "float"
});
gt_captcha_obj.appendTo("#GeetestCode");
gt_captcha_obj.onError(function(){
    pass_form.tips_text="Validate Error ";
    showTip();
});
gt_captcha_obj.onSuccess(function () {
    var validate = gt_captcha_obj.getValidate();
    console.log(validate);
});


function submitClick(){
    if(check()){
        var publicStr = $('#publicStr').val();
        var username=pass_form.username;
        var password=pass_form.password;
        var sha_password = sha256.hex(password);
        var sha_2password = CryptoJS.SHA512(sha_password).toString();
        username = cryptico.encrypt(username, publicStr).cipher;
        password = cryptico.encrypt(sha_2password, publicStr).cipher;
        $.post('/ajax/register',{
            user:username,
            password:password,
            validate:gt_captcha_obj.getValidate(),
            token: getCookie('token')
        },function(data,statu){
            if(data.code==1){
                location.href="/"
            }
            else{
                pass_form.tips_text=data.msg;
                showTip();
            }
        },'json');
    }
}

function check(){
    var validate = gt_captcha_obj.getValidate();
    console.log(validate);
    if(pass_form.username=="" || pass_form.password=="" || pass_form.password_again==""){
        pass_form.tips_text="Username and password can not be empty .";
    }
    else if(pass_form.username.length<3){
        pass_form.tips_text="Username is too short . At least 3";
    }
    else if(pass_form.password!=pass_form.password_again){
        pass_form.tips_text="Two passwords are not consistent .";
    }
    else if(pass_form.password.length<6){
        pass_form.tips_text="Password is too short . At least 6";
    }
    else if(!validate){
        pass_form.tips_text="Validate Fail .";
    }
    else
        return true;
    showTip();
    return false
}

function showTip(){
    $("#tips").removeClass("hide").hide()
    .slideDown(500,function(){
        setTimeout(function(){
            $("#tips").slideUp(300);
        },1800);
    });
}