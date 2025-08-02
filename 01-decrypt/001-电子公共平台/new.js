const CryptoJS = require('crypto-js');
function sign(t) {
    for (var e in t)
        "" !== t[e] && void 0 !== t[e] || delete t[e];
    var n = "B3978D054A72A7002063637CCDF6B2E5" + u(t);
    return s(n).toLocaleLowerCase()
}


function u(t) {
    for (var e = Object.keys(t).sort(l), n = "", a = 0; a < e.length; a++)
        if (void 0 !== t[e[a]])
            if (t[e[a]] && t[e[a]] instanceof Object || t[e[a]] instanceof Array) {
                var i = JSON.stringify(t[e[a]]);
                n += e[a] + i
            } else
                n += e[a] + t[e[a]];
    return n
}
function l(t, e) {
    return t.toString().toUpperCase() > e.toString().toUpperCase() ? 1 : t.toString().toUpperCase() == e.toString().toUpperCase() ? 0 : -1
}

function s(e) {
    return CryptoJS.MD5(e).toString()
}


// 解密函数
function decryptData(encryptedData) {
    // 将密钥和 IV 转换为 CryptoJS 格式
    const parsedKey = CryptoJS.enc.Utf8.parse("EB444973714E4A40876CE66BE45D5930");
    const parsedIv = CryptoJS.enc.Utf8.parse("B5A8904209931867");

    // 执行 AES 解密
    const decrypted = CryptoJS.AES.decrypt(encryptedData, parsedKey, {
        iv: parsedIv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });

    // 将解密结果转换为 UTF-8 字符串并返回
    return decrypted.toString(CryptoJS.enc.Utf8);
}