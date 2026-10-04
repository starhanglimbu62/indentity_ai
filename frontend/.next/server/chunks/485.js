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
/* harmony export */   x4: () => (/* binding */ login),
/* harmony export */   z2: () => (/* binding */ register)
/* harmony export */ });
const API_BASE = "http://127.0.0.1:8000" || 0;
async function request(path, options = {}) {
    const { auth = false, headers: customHeaders, ...requestOptions } = options;
    const headers = {
        Accept: "application/json"
    };
    if (customHeaders) {
        Object.assign(headers, customHeaders);
    }
    if (auth && "undefined" !== "undefined") {}
    const response = await fetch(`${API_BASE}${path}`, {
        ...requestOptions,
        headers
    });
    const text = await response.text();
    let data = null;
    try {
        data = text ? JSON.parse(text) : null;
    } catch  {
        data = text;
    }
    if (!response.ok) {
        const error = {
            status: response.status,
            data
        };
        throw error;
    }
    return data;
}
async function login(payload) {
    return request("/api/accounts/login/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });
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
async function verifyRequest(id, proof, publicSignals) {
    return request(`/api/verification/${id}/verify/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            proof,
            publicSignals
        }),
        auth: true
    });
}
const api = {
    request,
    login,
    register,
    uploadIdentity,
    createVerificationRequest,
    consentRequest,
    verifyRequest
};
/* unused harmony default export */ var __WEBPACK_DEFAULT_EXPORT__ = ((/* unused pure expression or super */ null && (api)));


/***/ })

};
;