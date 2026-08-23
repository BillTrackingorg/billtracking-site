import{$ as S,Aa as R,Da as w,Ea as N,Fa as _,K as c,L as h,N as u,Z as m,_ as E,aa as L,ha as $,ja as C,ka as p,ma as g,na as d,sa as x,ua as v,wa as W,xa as D,ya as M,za as O}from"./bt-chunk-AXBKUDUT.js";import{d as k,e as T,g as H,h as I,i as P,j as A}from"./bt-chunk-4PG7YGCE.js";import"./bt-chunk-SC6HPC6O.js";function Q(t){let e=S("web");return d`<h3 class="acct-eyebrow">${L.shownGroup}</h3>
<div class="acct-card">
  <p class="bt-row-cap bt-keyword-cap">${p.shownNote}</p>
  ${w(m.label,d`${m.caption}. <em>${$}</em>`,!1,g(' data-docket="1"'),{disabled:!0})}
</div>
<h3 class="acct-eyebrow">${p.docketGroup}</h3>
<div class="acct-card">
  <p class="acct-label">${C.head}</p>
  <p class="bt-row-cap bt-keyword-cap">${p.keywordsCaption}</p>
  ${N(t.keywords)}${_()}
</div>
<h3 class="acct-eyebrow">${p.displayGroup}</h3>
<div class="acct-card">
  ${E.map(n=>w(e[n].label,e[n].caption,t[n],g(` data-toggle="${n}"`)))}
  <p class="bt-foot">${p.foot}</p>
</div>`}function G(){let t=c("bt-settings-groups");if(!t||t.dataset.btWired)return;t.dataset.btWired="1";let e=D(),n=()=>h(t,Q(e)),s=i=>{e=i,M(e),n()};t.addEventListener("change",i=>{let o=i.target;if(!(o instanceof HTMLInputElement))return;let r=o.dataset.toggle;r&&s({...e,[r]:o.checked})});let a=()=>{let i=t.querySelector("input.bt-kw"),o=O(e,i?.value??"");if(!o){i&&(i.value="");return}s(o),t.querySelector("input.bt-kw")?.focus()};t.addEventListener("click",i=>{let o=i.target;if(!(o instanceof Element))return;if(o.closest(".bt-add")){a();return}let r=o.closest(".bt-chip-x");r?.dataset.keyword!==void 0&&s(R(e,r.dataset.keyword))}),t.addEventListener("keydown",i=>{if(i.key!=="Enter")return;let o=i.target;o instanceof HTMLInputElement&&o.classList.contains("bt-kw")&&(i.preventDefault(),a())}),n(),t.hidden=!1}var j="Your account",q=!1,B=!1;function K(t){for(let e of["loading","signed-out","signed-in"]){let n=c(`bt-acct-${e}`);n&&(n.hidden=e!==t)}}function z(t){let e=c("bt-acct-status");e&&(e.textContent=t)}function Y(t){let e=c("bt-provider-note");e&&(e.textContent=t)}function J(t){let e=[["google",c("bt-signin-google")],["apple",c("bt-signin-apple")]];for(let[n,s]of e)s instanceof HTMLButtonElement&&(s.disabled=!1,s.addEventListener("click",()=>{s.disabled=!0,Y(""),(async()=>{let a;try{a=await H(n,t)}catch{a={ok:!1,message:k[n]}}a.ok||(s.disabled=!1,Y(a.message))})()}))}function X(t){return d`<div class="acct-card acct-delete">
  <h2>${t.title}</h2>
  <p>${t.permanence}</p>
  <p>${t.published}</p>
  <p class="acct-note">${t.withoutAccount}</p>
  <p class="acct-status" role="status"></p>
  <div class="acct-buttons"><button type="button" class="btn-provider is-danger">${t.arm}</button></div>
</div>`}async function Z(){let{DELETE_ACCOUNT_COPY:t,appleFallbackNotice:e}=await import("./bt-auth-core-LM6BZBRE.js"),n=u(X(t)),s=n.querySelector(".acct-buttons"),a=n.querySelector(".acct-status"),i=()=>{a.textContent=t.confirmQuestion,s.replaceChildren(u(d`<button type="button" class="btn-provider is-danger">${t.confirm}</button>`),u(d`<button type="button" class="btn-provider">${t.cancel}</button>`));let[f,l]=Array.from(s.querySelectorAll("button"));l.addEventListener("click",()=>o()),f.addEventListener("click",()=>{f.disabled=!0,l.disabled=!0,(async()=>{let{deleteAccount:V}=await import("./bt-auth-core-LM6BZBRE.js"),b=await V();if(!b.ok){a.textContent=b.message,f.disabled=!1,l.disabled=!1;return}v(),r(b.appleRevocation)})()})},o=()=>{a.textContent="",s.replaceChildren(u(d`<button type="button" class="btn-provider is-danger">${t.arm}</button>`)),s.querySelector("button").addEventListener("click",()=>i())},r=f=>{let l=e(f);n.replaceChildren(u(d`<div>
  <h2>${t.doneTitle}</h2>
  <p>${t.doneBody}</p>${l?d`<p class="acct-note">${l}</p>`:""}
  <p>${t.doneAgain}</p>
  <div class="acct-buttons"><a class="btn-provider" href="/">${t.done}</a></div>
</div>`))};return o(),n}async function tt(t){let e=c("bt-acct-email");e&&(e.textContent=t.email??j);let n=c("bt-signout");n instanceof HTMLButtonElement&&!n.dataset.btWired&&(n.dataset.btWired="1",n.addEventListener("click",()=>{n.disabled=!0,(async()=>(await I(),v(),n.disabled=!1))()}));let s=c("bt-acct-signed-in");if(s&&!B){B=!0;let o=s.querySelector(".acct-danger"),r=await Z();o?o.before(r):s.appendChild(r)}let a=c("bt-geo-picker");a&&await x(a);let i=c("bt-consent-body");i&&await W(i)}var y=null;function U(t,e){if(t.status==="signed-in"){K("signed-in"),y!==t.userId&&(y=t.userId,tt(t)),e!=="/account"&&e!==location.pathname&&location.replace(e);return}y=null,K("signed-out")}function bt(){if(q)return;q=!0,G();let t=new URLSearchParams(location.search).get("next"),e=t?T(t):"/account";J(e),A(n=>{z(""),U(n,e)}),P().then(n=>U(n,e))}export{X as deleteCardIdleHtml,bt as mount};
