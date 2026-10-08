import{D as g,x as r,y as e}from"./bt-chunk-L3UMOCQA.js";import{D as d,E as N,F as S,H as b,I as T,J as x,m as h,v as p}from"./bt-chunk-XZZWEEQX.js";import{c as i}from"./bt-chunk-PYSTVWSS.js";var _={caption:S},I="bt-notif-panel",P=t=>`bt-notif-tab-${t}`,H=t=>t.join(">"),K=t=>t.split(">"),k=t=>`${i[t].names.short} tracker`;function E(t,s){let{row:o,path:a,isLeaf:f,scope:n}=s,$=a.length-1,l=H(a),m=t.open.has(l),u=k(t.selected),O=d.map(c=>{let y=x(c,t.switches,t.selected,a);return e`<span class="bt-tcell"><input type="checkbox" class="bt-tbox" data-row="${l}"
      data-col="${c}" data-state="${y}"${y==="on"?r(" checked"):r("")}
      aria-label="${b(o,n,u,c)}"></span>`}),w=f?e`<span class="bt-tex" aria-hidden="true"></span>`:e`<button type="button" class="bt-tex" data-open="${l}"
        aria-expanded="${m?"true":"false"}"
        aria-label="${b(o,n,u)}">${g(m?"chevron-down":"chevron-right")}</button>`;return e`<div class="bt-trow" data-depth="${String($)}">
    <div class="bt-tline">${w}<span class="bt-tlabel${$===0?" is-section":""}">${o.label}</span>${O}</div>
    <p class="bt-tcap">${o.caption}</p>
  </div>`}function C(){return e`<div class="bt-thead"><span class="bt-thgap"></span>${d.map(t=>e`<span class="bt-thcol">${N[t].head}</span>`)}</div>`}function F(t){return G({name:h(p.notifGroup),scope:t.scope,selected:t.selected,tabId:P,panelId:I})}function G(t){return t.scope.length===0?e``:t.scope.length===1?e`<p class="bt-tsolo" id="${t.tabId(t.selected)}">${k(t.selected)}</p>`:e`<div class="bt-tseg" role="tablist" aria-label="${t.name}">${t.scope.map(s=>e`<button type="button" role="tab" id="${t.tabId(s)}"
      data-polity="${s}"${t.mark??r("")} aria-controls="${t.panelId}"
      aria-selected="${s===t.selected?"true":"false"}"
      >${i[s].names.short}</button>`)}</div>`}function M(t){switch(t.state){case"signed-out":case"loading":case"failed":return e``;case"no-scope":return e``;case"ready":break;default:return t}let s=t.scope.length>1?"tabpanel":"group",o=e`${F(t)}<div class="bt-tree" id="${I}" role="${s}"
        aria-labelledby="${P(t.selected)}">${C()}${T(t.selected).filter(({path:a})=>a.every((f,n)=>n===a.length-1||t.open.has(H(a.slice(0,n+1))))).map(a=>E(t,a))}</div>`;return e`<h3 class="acct-eyebrow">${p.notifGroup}</h3>
<div class="acct-card bt-notif" data-polity="${t.selected}">
  <p class="bt-row-cap bt-keyword-cap">${_.caption}</p>
  ${o}
</div>`}export{K as a,G as b,M as c};
