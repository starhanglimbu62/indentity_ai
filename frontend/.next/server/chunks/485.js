"use strict";
exports.id = 485;
exports.ids = [485];
exports.modules = {

/***/ 9485:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   WA: () => (/* binding */ consentRequest),
/* harmony export */   ho: () => (/* binding */ uploadIdentity),
/* harmony export */   mA: () => (/* binding */ verifyRequest),
/* harmony export */   nY: () => (/* binding */ createVerificationRequest),
/* harmony export */   ou: () => (/* binding */ loginWithToken),
/* harmony export */   z2: () => (/* binding */ register)
/* harmony export */ });
const API_BASE = "http://localhost:8000" || 0;
async function request(path, opts = {}) {
    const url = `${API_BASE}${path}`;
    const headers = {
        "Accept": "application/json"
    };
    if (opts.headers) Object.assign(headers, opts.headers);
    if (opts.auth) {
        const token =  false ? 0 : null;
        if (token) headers["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(url, {
        ...opts,
        headers
    });
    const text = await res.text();
    let data = null;
    try {
        data = text ? JSON.parse(text) : null;
    } catch (e) {
        data = text;
    }
    if (!res.ok) {
        throw {
            status: res.status,
            data
        };
    }
    return data;
}
async function register(payload) {
    return request("/api/accounts/register/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });
}
async function loginWithToken(token) {
    // store token locally (no server call) - used for demo when user pastes a token
    localStorage.setItem("access", token);
    return {
        ok: true
    };
}
async function uploadIdentity(formData) {
    return request("/api/identity/documents/", {
        method: "POST",
        body: formData,
        auth: true
    });
}
async function createVerificationRequest(payload) {
    return request("/api/verification/request/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload),
        auth: true
    });
}
async function consentRequest(id) {
    return request(`/api/verification/${id}/consent/`, {
        method: "POST",
        auth: true
    });
}
async function verifyRequest(id) {
    return request(`/api/verification/${id}/verify/`, {
        method: "POST",
        auth: true
    });
}
/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = ({
    request
});


/***/ })

};
;