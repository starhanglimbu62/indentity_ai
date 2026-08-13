"use strict";
exports.id = 113;
exports.ids = [113];
exports.modules = {

/***/ 1113:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {


// EXPORTS
__webpack_require__.d(__webpack_exports__, {
  Z: () => (/* binding */ components_Layout)
});

// UNUSED EXPORTS: Layout

// EXTERNAL MODULE: ./node_modules/react/jsx-runtime.js
var jsx_runtime = __webpack_require__(5893);
// EXTERNAL MODULE: external "react"
var external_react_ = __webpack_require__(6689);
// EXTERNAL MODULE: ./node_modules/next/link.js
var next_link = __webpack_require__(1664);
var link_default = /*#__PURE__*/__webpack_require__.n(next_link);
// EXTERNAL MODULE: ./src/hooks/useAuth.tsx
var useAuth = __webpack_require__(7218);
;// CONCATENATED MODULE: ./src/components/NavBar.tsx



function NavBar() {
    const { token, setToken } = (0,useAuth/* useAuth */.a)();
    return /*#__PURE__*/ jsx_runtime.jsx("nav", {
        className: "bg-white shadow-sm",
        children: /*#__PURE__*/ (0,jsx_runtime.jsxs)("div", {
            className: "max-w-4xl mx-auto px-4 py-2 flex items-center justify-between",
            children: [
                /*#__PURE__*/ (0,jsx_runtime.jsxs)("div", {
                    className: "flex items-center gap-4",
                    children: [
                        /*#__PURE__*/ jsx_runtime.jsx((link_default()), {
                            href: "/",
                            className: "font-bold",
                            children: "IdentityAI"
                        }),
                        /*#__PURE__*/ jsx_runtime.jsx((link_default()), {
                            href: "/dashboard",
                            className: "text-sm text-gray-600",
                            children: "Dashboard"
                        })
                    ]
                }),
                /*#__PURE__*/ jsx_runtime.jsx("div", {
                    className: "flex items-center gap-3",
                    children: token ? /*#__PURE__*/ jsx_runtime.jsx("button", {
                        className: "text-sm text-red-600",
                        onClick: ()=>setToken(null),
                        children: "Logout"
                    }) : /*#__PURE__*/ (0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
                        children: [
                            /*#__PURE__*/ jsx_runtime.jsx((link_default()), {
                                href: "/login",
                                className: "text-sm",
                                children: "Login"
                            }),
                            /*#__PURE__*/ jsx_runtime.jsx((link_default()), {
                                href: "/register",
                                className: "text-sm",
                                children: "Register"
                            })
                        ]
                    })
                })
            ]
        })
    });
}

;// CONCATENATED MODULE: ./src/components/Layout.tsx



const Layout = ({ children })=>{
    return /*#__PURE__*/ (0,jsx_runtime.jsxs)("div", {
        className: "min-h-screen flex flex-col",
        children: [
            /*#__PURE__*/ jsx_runtime.jsx(NavBar, {}),
            /*#__PURE__*/ jsx_runtime.jsx("main", {
                className: "flex-1 max-w-4xl w-full mx-auto px-4 py-6",
                children: children
            })
        ]
    });
};
/* harmony default export */ const components_Layout = (Layout);


/***/ })

};
;