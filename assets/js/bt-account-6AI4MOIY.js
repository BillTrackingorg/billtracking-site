import{$ as C,Da as S,Ea as K,Fa as Y,K as d,L as T,N as m,Z as h,_ as k,aa as w,ha as H,ja as A,ka as b,ma as u,na as l,pa as R,qa as g,sa as N,ta as D,va as U,wa as q,xa as G,ya as B,za as V}from"./bt-chunk-IMPMHD6W.js";import{c as P,d as I,e as M,g as W,h as _,i as x,j as O}from"./bt-chunk-HUYIAOT6.js";import"./bt-chunk-EFY6G3MJ.js";var F="Not set",ot="Country",nt="State",y=(t,e,o)=>l`<option value="${t}"${o?u(" selected"):u("")}>${e}</option>`;async function Q(t){let e=null;try{e=await R()}catch{t.replaceChildren(m(l`<p class="acct-note">We couldn’t read your account record just now. This is a connection problem, not an answer — nothing has changed.</p>`));return}let o=e!==null,a=e?.country??"",i=e?.usState??"",n=m(l`<div class="geo-picker">
  <label class="geo-field">
    <span class="geo-label">${ot}</span>
    <select class="geo-select" name="country"${o?u(""):u(" disabled")}>${[y("",F,a==="")].concat(D.map(c=>y(c.code,`${c.flag} ${c.name}`,c.code===a)))}</select>
  </label>
  <label class="geo-field"${a==="US"?u(""):u(" hidden")}>
    <span class="geo-label">${nt}</span>
    <select class="geo-select" name="us_state"${o?u(""):u(" disabled")}>${[y("",F,i==="")].concat(U.map(c=>y(c.code,c.name,c.code===i)))}</select>
  </label>
  <p class="acct-note geo-status" role="status">${o?"":"This becomes editable after your first vote \u2014 that is when your account record is created, and this is stored on it."}</p>
</div>`),s=n.querySelector('select[name="country"]'),r=n.querySelector('select[name="us_state"]'),f=r.closest(".geo-field"),p=n.querySelector(".geo-status"),v=async()=>{let c=s.value||void 0,L=c==="US"&&r.value||void 0;p.textContent="Saving\u2026",await P();let $=await(await import("./bt-voter-S554PBNF.js")).setVoterLocation({...c?{country:c}:{},...L?{usState:L}:{}});g(),p.textContent=$.ok?"Saved.":$.message};s.addEventListener("change",()=>{let c=s.value==="US";f.hidden=!c,c||(r.value=""),v()}),r.addEventListener("change",()=>{v()}),t.replaceChildren(n)}function st(t){let e=C("web");return l`<h3 class="acct-eyebrow">${w.shownGroup}</h3>
<div class="acct-card">
  <p class="bt-row-cap bt-keyword-cap">${b.shownNote}</p>
  ${S(h.label,l`${h.caption}. <em>${H}</em>`,!1,u(' data-docket="1"'),{disabled:!0})}
</div>
<h3 class="acct-eyebrow">${b.docketGroup}</h3>
<div class="acct-card">
  <p class="acct-label">${A.head}</p>
  <p class="bt-row-cap bt-keyword-cap">${b.keywordsCaption}</p>
  ${K(t.keywords)}${Y()}
</div>
<h3 class="acct-eyebrow">${w.displayGroup}</h3>
<div class="acct-card">
  ${k.map(o=>S(e[o].label,e[o].caption,t[o],u(` data-toggle="${o}"`)))}
  <p class="bt-foot">${b.foot}</p>
</div>`}function z(){let t=d("bt-settings-groups");if(!t||t.dataset.btWired)return;t.dataset.btWired="1";let e=q(),o=()=>T(t,st(e)),a=n=>{e=n,G(e),o()};t.addEventListener("change",n=>{let s=n.target;if(!(s instanceof HTMLInputElement))return;let r=s.dataset.toggle;r&&a({...e,[r]:s.checked})});let i=()=>{let n=t.querySelector("input.bt-kw"),s=B(e,n?.value??"");if(!s){n&&(n.value="");return}a(s),t.querySelector("input.bt-kw")?.focus()};t.addEventListener("click",n=>{let s=n.target;if(!(s instanceof Element))return;if(s.closest(".bt-add")){i();return}let r=s.closest(".bt-chip-x");r?.dataset.keyword!==void 0&&a(V(e,r.dataset.keyword))}),t.addEventListener("keydown",n=>{if(n.key!=="Enter")return;let s=n.target;s instanceof HTMLInputElement&&s.classList.contains("bt-kw")&&(n.preventDefault(),i())}),o(),t.hidden=!1}var at="Your account",J=!1,X=!1;function Z(t){for(let e of["loading","signed-out","signed-in"]){let o=d(`bt-acct-${e}`);o&&(o.hidden=e!==t)}}function ct(t){let e=d("bt-acct-status");e&&(e.textContent=t)}function tt(t){let e=d("bt-provider-note");e&&(e.textContent=t)}function it(t){let e=[["google",d("bt-signin-google")],["apple",d("bt-signin-apple")]];for(let[o,a]of e)a instanceof HTMLButtonElement&&(a.disabled=!1,a.addEventListener("click",()=>{a.disabled=!0,tt(""),(async()=>{let i;try{i=await W(o,t)}catch{i={ok:!1,message:I[o]}}i.ok||(a.disabled=!1,tt(i.message))})()}))}async function rt(){let{DELETE_ACCOUNT_COPY:t,appleFallbackNotice:e}=await import("./bt-auth-core-5AIEQ2CK.js"),o=m(l`<section class="acct-card acct-delete">
  <h2>${t.title}</h2>
  <p>${t.permanence}</p>
  <p>${t.published}</p>
  <p class="acct-note">${t.withoutAccount}</p>
  <p class="acct-status" role="status"></p>
  <div class="acct-buttons"></div>
</section>`),a=o.querySelector(".acct-buttons"),i=o.querySelector(".acct-status"),n=()=>{i.textContent=t.confirmQuestion,a.replaceChildren(m(l`<button type="button" class="btn-provider is-danger">${t.confirm}</button>`),m(l`<button type="button" class="btn-provider">${t.cancel}</button>`));let[f,p]=Array.from(a.querySelectorAll("button"));p.addEventListener("click",()=>s()),f.addEventListener("click",()=>{f.disabled=!0,p.disabled=!0,(async()=>{let{deleteAccount:v}=await import("./bt-auth-core-5AIEQ2CK.js"),c=await v();if(!c.ok){i.textContent=c.message,f.disabled=!1,p.disabled=!1;return}g(),r(c.appleRevocation)})()})},s=()=>{i.textContent="",a.replaceChildren(m(l`<button type="button" class="btn-provider is-danger">${t.arm}</button>`)),a.querySelector("button").addEventListener("click",()=>n())},r=f=>{let p=e(f);o.replaceChildren(m(l`<div>
  <h2>${t.doneTitle}</h2>
  <p>${t.doneBody}</p>${p?l`<p class="acct-note">${p}</p>`:""}
  <p>${t.doneAgain}</p>
  <div class="acct-buttons"><a class="btn-provider" href="/">${t.done}</a></div>
</div>`))};return s(),o}async function lt(t){let e=d("bt-acct-email");e&&(e.textContent=t.email??at);let o=d("bt-signout");o instanceof HTMLButtonElement&&!o.dataset.btWired&&(o.dataset.btWired="1",o.addEventListener("click",()=>{o.disabled=!0,(async()=>(await _(),g(),o.disabled=!1))()}));let a=d("bt-acct-signed-in");if(a&&!X){X=!0;let s=a.querySelector(".acct-danger"),r=await rt();s?s.before(r):a.appendChild(r)}let i=d("bt-geo-picker");i&&await Q(i);let n=d("bt-consent");n&&await N(n)}var E=null;function et(t,e){if(t.status==="signed-in"){Z("signed-in"),E!==t.userId&&(E=t.userId,lt(t)),e!=="/account"&&e!==location.pathname&&location.replace(e);return}E=null,Z("signed-out")}function It(){if(J)return;J=!0,z();let t=M(new URLSearchParams(location.search).get("next"));it(t),O(e=>{ct(""),et(e,t)}),x().then(e=>et(e,t))}export{It as mount};
