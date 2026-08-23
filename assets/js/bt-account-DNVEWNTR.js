import{$ as L,Aa as R,Da as y,Ea as G,Fa as q,K as c,L as S,N as u,Z as b,_ as C,aa as $,ha as k,ja as T,ka as p,ma as g,na as d,sa as W,ua as w,wa as N,xa as D,ya as M,za as _}from"./bt-chunk-NYPOLYMQ.js";import{d as H,e as A,g as I,h as P,i as v,j as x,k as O}from"./bt-chunk-34H5OVTL.js";import"./bt-chunk-R6J2KOPC.js";function z(t){let e=L("web");return d`<h3 class="acct-eyebrow">${$.shownGroup}</h3>
<div class="acct-card">
  <p class="bt-row-cap bt-keyword-cap">${p.shownNote}</p>
  ${y(b.label,d`${b.caption}. <em>${k}</em>`,!1,g(' data-docket="1"'),{disabled:!0})}
</div>
<h3 class="acct-eyebrow">${p.docketGroup}</h3>
<div class="acct-card">
  <p class="acct-label">${T.head}</p>
  <p class="bt-row-cap bt-keyword-cap">${p.keywordsCaption}</p>
  ${G(t.keywords)}${q()}
</div>
<h3 class="acct-eyebrow">${p.displayGroup}</h3>
<div class="acct-card">
  ${C.map(n=>y(e[n].label,e[n].caption,t[n],g(` data-toggle="${n}"`)))}
  <p class="bt-foot">${p.foot}</p>
</div>`}function B(){let t=c("bt-settings-groups");if(!t||t.dataset.btWired)return;t.dataset.btWired="1";let e=D(),n=()=>S(t,z(e)),i=s=>{e=s,M(e),n()};t.addEventListener("change",s=>{let o=s.target;if(!(o instanceof HTMLInputElement))return;let r=o.dataset.toggle;r&&i({...e,[r]:o.checked})});let a=()=>{let s=t.querySelector("input.bt-kw"),o=_(e,s?.value??"");if(!o){s&&(s.value="");return}i(o),t.querySelector("input.bt-kw")?.focus()};t.addEventListener("click",s=>{let o=s.target;if(!(o instanceof Element))return;if(o.closest(".bt-add")){a();return}let r=o.closest(".bt-chip-x");r?.dataset.keyword!==void 0&&i(R(e,r.dataset.keyword))}),t.addEventListener("keydown",s=>{if(s.key!=="Enter")return;let o=s.target;o instanceof HTMLInputElement&&o.classList.contains("bt-kw")&&(s.preventDefault(),a())}),n(),t.hidden=!1}var J="Your account",K=!1,U=!1;function Y(t){for(let e of["loading","signed-out","signed-in"]){let n=c(`bt-acct-${e}`);n&&(n.hidden=e!==t)}}function X(t){let e=c("bt-acct-status");e&&(e.textContent=t)}function V(t){let e=c("bt-provider-note");e&&(e.textContent=t)}function Z(t){let e=[["google",c("bt-signin-google")],["apple",c("bt-signin-apple")]];for(let[n,i]of e)i instanceof HTMLButtonElement&&(i.disabled=!1,i.addEventListener("click",()=>{i.disabled=!0,V(""),(async()=>{let a;try{a=await I(n,t)}catch{a={ok:!1,message:H[n]}}a.ok||(i.disabled=!1,V(a.message))})()}))}function tt(t){return d`<div class="acct-card acct-delete">
  <h2>${t.title}</h2>
  <p>${t.permanence}</p>
  <p>${t.published}</p>
  <p class="acct-note">${t.withoutAccount}</p>
  <p class="acct-status" role="status"></p>
  <div class="acct-buttons"><button type="button" class="btn-provider is-danger">${t.arm}</button></div>
</div>`}async function et(){let{DELETE_ACCOUNT_COPY:t,appleFallbackNotice:e}=await import("./bt-auth-core-Q6PHPBLR.js"),n=u(tt(t)),i=n.querySelector(".acct-buttons"),a=n.querySelector(".acct-status"),s=()=>{a.textContent=t.confirmQuestion,i.replaceChildren(u(d`<button type="button" class="btn-provider is-danger">${t.confirm}</button>`),u(d`<button type="button" class="btn-provider">${t.cancel}</button>`));let[f,l]=Array.from(i.querySelectorAll("button"));l.addEventListener("click",()=>o()),f.addEventListener("click",()=>{f.disabled=!0,l.disabled=!0,(async()=>{let{deleteAccount:Q}=await import("./bt-auth-core-Q6PHPBLR.js"),m=await Q();if(!m.ok){a.textContent=m.message,f.disabled=!1,l.disabled=!1;return}w(),r(m.appleRevocation)})()})},o=()=>{a.textContent="",i.replaceChildren(u(d`<button type="button" class="btn-provider is-danger">${t.arm}</button>`)),i.querySelector("button").addEventListener("click",()=>s())},r=f=>{let l=e(f);n.replaceChildren(u(d`<div>
  <h2>${t.doneTitle}</h2>
  <p>${t.doneBody}</p>${l?d`<p class="acct-note">${l}</p>`:""}
  <p>${t.doneAgain}</p>
  <div class="acct-buttons"><a class="btn-provider" href="/">${t.done}</a></div>
</div>`))};return o(),n}async function nt(t){(async()=>{if(await P()!=="gone")return;let{ACCOUNT_GONE_NOTICE:o}=await import("./bt-auth-core-Q6PHPBLR.js");E=o,await v()})();let e=c("bt-acct-email");e&&(e.textContent=t.email??J);let n=c("bt-signout");n instanceof HTMLButtonElement&&!n.dataset.btWired&&(n.dataset.btWired="1",n.addEventListener("click",()=>{n.disabled=!0,(async()=>(await v(),w(),n.disabled=!1))()}));let i=c("bt-acct-signed-in");if(i&&!U){U=!0;let o=i.querySelector(".acct-danger"),r=await et();o?o.before(r):i.appendChild(r)}let a=c("bt-geo-picker");a&&await W(a);let s=c("bt-consent-body");s&&await N(s)}var h=null,E=null;function F(t,e){if(t.status==="signed-in"){Y("signed-in"),h!==t.userId&&(h=t.userId,nt(t)),e!=="/account"&&e!==location.pathname&&location.replace(e);return}h=null,Y("signed-out")}function gt(){if(K)return;K=!0,B();let t=new URLSearchParams(location.search).get("next"),e=t?A(t):"/account";Z(e),O(n=>{n.status==="signed-in"&&(E=null),X(E??""),F(n,e)}),x().then(n=>F(n,e))}export{tt as deleteCardIdleHtml,gt as mount};
