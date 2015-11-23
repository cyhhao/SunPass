/**
 * Created by cyh on 2015/11/9.
 */

var RSA_Bits=512;
var RSA_textMax=RSA_Bits/8-11;
var publicKeyFromString = function (string) {
    var tokens = string.split("|");
    var N = tokens[0];
    var E = tokens.length > 1 ? tokens[1] : "03";
    var rsa = new RSAKey();
    rsa.setPublic(N, E);
    return rsa
};
function _splitStr(text, length) {
    var list = [];
    for (var i = 0; i < text.length / length; i++) {
        list.push(text.substr(i * length, length));
    }
    return list;
}
cryptico.encrypt = function (plaintext, publickeystring) {
    var cipherblock = "";
    try {
        var publickey = publicKeyFromString(publickeystring);
        var list = _splitStr(plaintext, RSA_textMax);
        for (var i = 0; i < list.length; i++) {
            if (i >= 1) cipherblock += '|';
            cipherblock += cryptico.b16to64(publickey.encrypt(list[i]));
        }
    }
    catch (err) {
        return {status: "Invalid public key" + " " + err};
    }
    return {status: "success", cipher: cipherblock};
};
cryptico.decrypt = function (ciphertext, key) {
    var list = ciphertext.split('|');
    var Str = "";
    for (var i = 0; i < list.length; i++) {
        Str += key.decrypt(cryptico.b64to16(list[i]));
    }

    var plaintext = Str;
    if (plaintext == null) {
        return {status: "failure"};
    }
    else {
        return {
            status: "success",
            plaintext: plaintext
        }
    }
};
function sha2aeskey(sha) {
    return cryptico.b256to64(sha).slice(0, 32)
}
window.getCookie = function (name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
};