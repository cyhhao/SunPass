/**
 * Created by cyh on 2015/11/9.
 */

Vue.config.delimiters = ['[[', ']]'];
Vue.filter("ZHstatus", function (status, which, type) {
    if (type == "class") {
        if (status == which)return "";
        else return "hide";
    }
    else if (type == 'readonly') {
        return status == 'show';
    }
    else if (type == 'title') {
        if (status == 'show') return "click to go";
        else return "";
    }
});

Vue.directive('readonly', {
    update: function (value) {
        if (value) {
            $(this.el).attr("readonly", "true");
        }
        else {
            $(this.el).removeAttr("readonly");
        }
    }
});

var pass_list = new Vue({
    el: '#pass_list',
    data: {
        items: []
    },
    methods: {
        addClick: function () {
            pass_list.items.push({
                model: {
                    id: sha256.hex(String(Math.random())),
                    label: "",
                    url: "",
                    user: "",
                    password: randPassword()
                },
                control: {old_model: {}, status: "edit"}
            });
            Vue.nextTick(function () {
                bindCopy($('.copy'));
            });
        },
        deleteClick: function (index, item) {
            if (window.confirm('Are you sure ?')) {

                $.post('/ajax/deletePass', {
                    token: getCookie('token'),
                    id: item.model.id
                }, function (data, status) {
                    if (data.code == 1) {
                        pass_list.items.splice(index, 1)
                    }
                    Vue.nextTick(function () {
                        bindCopy($('.copy'));
                    });
                }, 'json');
            }

        },
        labelClick: function (item) {
            if (item.model.url != "" && item.control.status == 'show')
                window.open(item.model.url);
        },
        editClick: function (item) {
            item.control.status = "edit";
            item.control.old_model = JSON.parse(JSON.stringify(item.model));
        },
        closeClick: function (item) {
            item.control.status = "show";
            item.model = JSON.parse(JSON.stringify(item.control.old_model));
        },
        saveClick: function (item) {
            var count = 0;
            var mystr = item.model.label + item.model.user;
            for (it in pass_list.items) {
                var tem = pass_list.items[it].model.label + pass_list.items[it].model.user;
                if (tem == mystr) {
                    count++;
                }
            }
            if (!/http:\/\//.test(item.model.url) && !/https:\/\//.test(item.model)) {
                item.model.url = "http://" + item.model.url;
            }

            if (count >= 2) {
                alert("Can't save ! You have the same label and user item .");
            }
            else if (item.model.label == "" || item.model.user == "") {
                alert("Can't save !  Label and user couldn't be empty .")
            }
            else {
                var publicStr = $('#publicStr').val();
                //item.model.password
                var e_text = cryptico.encryptAESCBC(encode64(utf16to8(JSON.stringify(item.model))), sha2aeskey(sessionStorage.password))
                e_text += "|" + item.model.id;

                var model = cryptico.encrypt(e_text, publicStr).cipher;
                $.post('/ajax/editPass', {
                    token: getCookie('token'),
                    item: model
                }, function (data, status) {
                    if (data.code == 1) {
                        item.control.status = "show";
                    }
                    else {
                        alert(data.msg);
                    }
                }, 'json');
            }
        },
        randomClick: function (item) {
            item.model.password = randPassword();
        },
        logoutClick: function () {
            $.post('/logout', {
                token: getCookie('token')
            }, function (data) {
                if (data.code == 1) {
                    sessionStorage.password = null;
                    window.location.href = location.href;
                }
                else {
                    alert(data.msg);
                }
            }, 'json')
        }
    }
});
function randPassword() {
    var text = ['abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '1234567890', '~!@#$%^&*()_+";",./?<>'];
    var rand = function (min, max) {
        return parseInt(min + Math.random() * (max - min + 1))
    };
    var len = rand(8, 16);
    var pw = '';
    for (var i = 0; i < len; ++i) {
        var strpos = rand(0, 3);
        pw += text[strpos].charAt(rand(0, text[strpos].length - 1));
    }
    return pw;
}
client = null;
function bindCopy(list) {
    $('[data-toggle="tooltip"]').tooltip();
    if (client) client.destroy();
    client = new ZeroClipboard(list);
    client.on("ready", function (readyEvent) {
        client.on("aftercopy", function (event) {
            $('#myModal').modal('show');
            setTimeout(function () {
                $('#myModal').modal('hide');
            }, 1000);
        });
    });

}

$(document).ready(function () {
    // The passphrase used to repeatably generate this RSA key.
    var PassPhrase = "" + Math.random();
    // The length of the RSA key, in bits.
    var Bits = 1024;
    var MattsRSAkey = cryptico.generateRSAKey(PassPhrase, Bits);

    $.post('/ajax/getPass', {
        token: getCookie('token'),
        n: String(MattsRSAkey.n),
        e: String(MattsRSAkey.e)
    }, function (data, status) {
        if (data.code == 1) {
            var DecryptionResult = cryptico.decrypt(String(data.data), MattsRSAkey);
            var base = DecryptionResult.plaintext;
            var dict = JSON.parse(base);
            //var models=[];
            pass_list.items = [];
            for (var i in dict) {
                var ans = cryptico.decryptAESCBC(dict[i], sha2aeskey(sessionStorage.password));
                var de_base = utf8to16(decode64(ans));
                pass_list.items.push({
                    model: JSON.parse(de_base),
                    control: {old_model: {}, status: "show"}
                });
            }
            Vue.nextTick(function () {
                $('.datarow').removeClass("hide");
                $('.loading').addClass("hide");
                bindCopy($('.copy'));
            });
        }
        else {
            alert("Failed to get the password . Try to refresh this page")
        }
    }, 'json');
});