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
// EXTERNAL MODULE: external "next/router"
var router_ = __webpack_require__(1853);
// EXTERNAL MODULE: ./src/hooks/useAuth.tsx
var useAuth = __webpack_require__(7218);
;// CONCATENATED MODULE: ./src/components/NavBar.tsx




function NavBar() {
    const { token, setToken } = (0,useAuth/* useAuth */.a)();
    const router = (0,router_.useRouter)();
    const links = [
        {
            href: "/dashboard",
            label: "Dashboard"
        },
        {
            href: "/credentials",
            label: "Credentials"
        },
        {
            href: "/requests",
            label: "Requests"
        }
    ];
    return /*#__PURE__*/ jsx_runtime.jsx("nav", {
        className: "sticky top-0 z-10 border-b border-slate-200/80 bg-white/90 backdrop-blur",
        children: /*#__PURE__*/ (0,jsx_runtime.jsxs)("div", {
            className: "mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8",
            children: [
                /*#__PURE__*/ (0,jsx_runtime.jsxs)("div", {
                    className: "flex min-w-0 items-center gap-6",
                    children: [
                        /*#__PURE__*/ (0,jsx_runtime.jsxs)((link_default()), {
                            href: "/",
                            className: "flex items-center gap-2 text-lg font-bold tracking-tight text-slate-950",
                            children: [
                                /*#__PURE__*/ jsx_runtime.jsx("span", {
                                    className: "flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-sm text-white",
                                    children: "I"
                                }),
                                /*#__PURE__*/ jsx_runtime.jsx("span", {
                                    children: "IdentityAI"
                                })
                            ]
                        }),
                        token && /*#__PURE__*/ jsx_runtime.jsx("div", {
                            className: "hidden items-center gap-1 md:flex",
                            children: links.map((link)=>/*#__PURE__*/ jsx_runtime.jsx((link_default()), {
                                    href: link.href,
                                    className: `rounded-lg px-3 py-2 text-sm font-medium transition ${router.pathname.startsWith(link.href) ? "bg-indigo-50 text-indigo-700" : "text-slate-500 hover:bg-slate-100 hover:text-slate-900"}`,
                                    children: link.label
                                }, link.href))
                        })
                    ]
                }),
                /*#__PURE__*/ jsx_runtime.jsx("div", {
                    className: "flex shrink-0 items-center gap-3",
                    children: token ? /*#__PURE__*/ jsx_runtime.jsx("button", {
                        className: "rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700",
                        onClick: ()=>setToken(null),
                        children: "Log out"
                    }) : /*#__PURE__*/ (0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
                        children: [
                            /*#__PURE__*/ jsx_runtime.jsx((link_default()), {
                                href: "/login",
                                className: "hidden text-sm font-medium text-slate-600 hover:text-slate-950 sm:block",
                                children: "Log in"
                            }),
                            /*#__PURE__*/ jsx_runtime.jsx((link_default()), {
                                href: "/register",
                                className: "rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700",
                                children: "Create account"
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
                className: "flex-1 w-full max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8",
                children: children
            }),
            /*#__PURE__*/ jsx_runtime.jsx("footer", {
                className: "px-4 py-6 text-center text-xs text-slate-400 sm:px-6",
                children: "Privacy-first identity verification"
            })
        ]
    });
};
/* harmony default export */ const components_Layout = (Layout);


/***/ })

};
;